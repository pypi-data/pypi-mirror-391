import asyncio
import json
from typing import Literal

import aiohttp
import pydantic

try:
    import transformers  # ty: ignore[unresolved-import]
except ModuleNotFoundError:
    transformers = None  # ty: ignore[invalid-assignment]

try:
    import vllm  # ty: ignore[unresolved-import]
except ModuleNotFoundError:
    vllm = None  # ty: ignore[invalid-assignment]

from ..modeling import (
    AIServiceDescription,
    ScopeClass,
    ScopeClassification,
    ScopeClassificationInput,
)
from ..prompting import prepare_messages
from .base import MODELS, AsyncScopeClassifier, ScopeClassifier


def _build_prompt(
    tokenizer,
    conversation: ScopeClassificationInput,
    ai_service_description: str | AIServiceDescription,
    skip_evidences: bool,
) -> str:
    messages = prepare_messages(
        conversation,
        ai_service_description,
        skip_evidences,
    )
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    return prompt


@ScopeClassifier.register_classifier("vllm")
class VLLMScopeClassifier(ScopeClassifier):
    def __init__(
        self,
        backend: Literal["vllm"] = "vllm",
        model: MODELS | str = "small",
        skip_evidences: bool = False,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        max_model_len: int = 10_000,
        max_num_seqs: int = 2,
    ):
        if transformers is None:
            raise ImportError("transformers is not installed")

        if vllm is None:
            raise ImportError("vllm is not installed")

        super().__init__(backend)
        self.model = self.maybe_map_model(model)
        self.skip_evidences = skip_evidences
        self.llm = vllm.LLM(
            model=self.model, max_model_len=max_model_len, max_num_seqs=max_num_seqs
        )
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(self.model)
        self.sampling_params = vllm.SamplingParams(
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _classify(
        self,
        conversation: ScopeClassificationInput,
        ai_service_description: str | AIServiceDescription,
        skip_evidences: bool | None = None,
    ) -> ScopeClassification:
        return self._batch_classify(
            [conversation], ai_service_description, skip_evidences=skip_evidences
        )[0]

    def _batch_classify(
        self,
        conversations: list[ScopeClassificationInput],
        ai_service_description: str | AIServiceDescription | None = None,
        ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
        skip_evidences: bool | None = None,
    ) -> list[ScopeClassification]:
        if ai_service_descriptions is not None:
            prompts = [
                _build_prompt(
                    self.tokenizer,
                    c,
                    ad,
                    skip_evidences=skip_evidences
                    if skip_evidences is not None
                    else self.skip_evidences,
                )
                for c, ad in zip(conversations, ai_service_descriptions)
            ]
        elif ai_service_description is not None:
            prompts = [
                _build_prompt(
                    self.tokenizer,
                    c,
                    ai_service_description,
                    skip_evidences=skip_evidences
                    if skip_evidences is not None
                    else self.skip_evidences,
                )
                for c in conversations
            ]
        else:
            raise ValueError

        outputs = self.llm.generate(prompts, self.sampling_params, use_tqdm=False)

        results = []

        for output in outputs:
            text = output.outputs[0].text

            # TODO generation errors: handle potentially invalid JSON (retry?)
            parsed_obj = json.loads(text)

            # TODO generation errors: handle model validation failure (retry?)
            results.append(
                ScopeClassification(
                    evidences=parsed_obj.get("evidences"),
                    scope_class=ScopeClass(parsed_obj["scope_class"]),
                )
            )

        return results


@AsyncScopeClassifier.register_classifier("vllm-async-api")
class VLLMAsyncApiScopeClassifier(AsyncScopeClassifier):
    def __init__(
        self,
        backend: Literal["api"] = "api",
        model: MODELS | str = "small",
        skip_evidences: bool = False,
        vllm_serving_url: str = "http://localhost:8000",
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ):
        super().__init__(backend)
        self.model = self.maybe_map_model(model)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(self.model)
        self.skip_evidences = skip_evidences
        self.vllm_serving_url = vllm_serving_url
        self.vllm_temperature = temperature
        self.vllm_max_tokens = max_tokens

    async def _classify(
        self,
        conversation: ScopeClassificationInput,
        ai_service_description: str | AIServiceDescription,
        skip_evidences: bool | None = None,
    ) -> ScopeClassification:
        results = await self._batch_classify(
            [conversation], ai_service_description, skip_evidences=skip_evidences
        )
        return results[0]

    async def _handle_request(
        self,
        session: aiohttp.ClientSession,
        prompt: str,
    ) -> ScopeClassification:
        async with session.post(
            f"{self.vllm_serving_url}/v1/completions",
            json={
                "model": self.model,
                "prompt": prompt,
                "temperature": self.vllm_temperature,
                "max_tokens": self.vllm_max_tokens,
            },
            headers={"Content-Type": "application/json"},
        ) as response:
            response.raise_for_status()
            response_json = await response.json()

        try:
            parsed_obj = json.loads(response_json["choices"][0]["text"])
        except json.JSONDecodeError:
            # TODO generation errors: handle potentially invalid JSON (retry?)
            raise ValueError(f"Failed to parse generated text: {response_json['text']}")

        try:
            validated_obj = ScopeClassification.model_validate(parsed_obj)
        except pydantic.ValidationError as e:
            # TODO generation errors: handle model validation failure (retry?)
            raise ValueError(f"Failed to validate generated text: {e}")

        return validated_obj

    async def _batch_classify(
        self,
        conversations: list[ScopeClassificationInput],
        ai_service_description: str | AIServiceDescription | None = None,
        ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
        skip_evidences: bool | None = None,
    ) -> list[ScopeClassification]:
        if ai_service_description is not None:
            ai_service_descriptions = [ai_service_description] * len(conversations)  # type: ignore[invalid-assignment]

        async with aiohttp.ClientSession() as session:
            tasks = [
                self._handle_request(
                    session,
                    _build_prompt(
                        self.tokenizer,
                        conv,
                        desc,
                        skip_evidences=skip_evidences
                        if skip_evidences is not None
                        else self.skip_evidences,
                    ),
                )
                for conv, desc in zip(conversations, ai_service_descriptions)  # type: ignore[invalid-argument-type]
            ]
            results = await asyncio.gather(*tasks)

        return results
