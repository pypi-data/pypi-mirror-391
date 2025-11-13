import json
from dataclasses import dataclass
from typing import Literal

import pydantic

try:
    import torch  # ty: ignore[unresolved-import]
except ModuleNotFoundError:
    torch = None  # ty: ignore[invalid-assignment]

try:
    import transformers  # ty: ignore[unresolved-import]
    from transformers import Pipeline  # ty: ignore[unresolved-import]
except ModuleNotFoundError:
    transformers = None  # ty: ignore[invalid-assignment]

    class Pipeline:
        pass


from ..modeling import (
    AIServiceDescription,
    ScopeClass,
    ScopeClassification,
    ScopeClassificationInput,
)
from ..prompting import prepare_messages
from .base import MODELS, ScopeClassifier


@dataclass
class PipelineInputs:
    coonversation: ScopeClassificationInput
    ai_service_description: str | AIServiceDescription


class HuggingFaceScopeClassificationPipeline(Pipeline):  # type: ignore[unsupported-base]
    def __init__(
        self,
        model,
        tokenizer=None,
        skip_evidences: bool = False,
        max_new_tokens: int = 1024,
        do_sample: bool = False,
        **kwargs,
    ):
        if tokenizer is None and isinstance(model, str):
            tokenizer = transformers.AutoTokenizer.from_pretrained(model)
        elif isinstance(tokenizer, str):
            tokenizer = transformers.AutoTokenizer.from_pretrained(tokenizer)

        if isinstance(model, str):
            model = transformers.AutoModelForCausalLM.from_pretrained(
                model, dtype="auto", device_map="auto"
            )

        # Set left padding for decoder-only models (required for batched generation)
        if tokenizer is not None:
            tokenizer.padding_side = "left"
            # Ensure pad token is set (use eos_token if pad_token doesn't exist)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

        self.skip_evidences = skip_evidences
        self.max_new_tokens = max_new_tokens
        self.do_sample = do_sample

        super().__init__(model, tokenizer, **kwargs)

    def _sanitize_parameters(
        self,
        **kwargs,
    ):
        preprocess_kwargs = {}
        if "skip_evidences" in kwargs or self.skip_evidences:
            preprocess_kwargs["skip_evidences"] = kwargs.get(
                "skip_evidences", self.skip_evidences
            )

        return (
            preprocess_kwargs,
            {},
            {},
        )

    def preprocess(
        self,
        inputs: PipelineInputs,
        skip_evidences: bool = False,
    ):
        model_messages = prepare_messages(
            inputs.coonversation,
            inputs.ai_service_description,
            skip_evidences,
        )

        text = self.tokenizer.apply_chat_template(
            model_messages,
            tokenize=False,  # we are not tokenizing so as to enable batching
            add_generation_prompt=True,
            enable_thinking=False,
        )

        return {"text": text}

    def _forward(self, model_inputs):
        tokenized = self.tokenizer(
            model_inputs["text"],
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(self.device)

        with torch.inference_mode():
            outputs = self.model.generate(
                **tokenized,
                max_new_tokens=self.max_new_tokens,
                do_sample=self.do_sample,
            )
        return {
            "output_ids": outputs,
            "input_ids": tokenized["input_ids"],
        }

    def postprocess(self, model_outputs):
        output_ids = model_outputs["output_ids"]
        input_ids = model_outputs["input_ids"]

        # Decode each output in the batch
        results = []
        for i in range(output_ids.shape[0]):
            # Skip the input tokens to get only the generated text
            generated_ids = output_ids[i][input_ids.shape[1] :]
            generated_output = self.tokenizer.decode(
                generated_ids,
                skip_special_tokens=True,
            )
            results.append({"generated_text": generated_output})

        return results


@ScopeClassifier.register_classifier("hf")
class HuggingFaceScopeClassifier(ScopeClassifier):
    def __init__(
        self,
        backend: Literal["hf"] = "hf",
        model: MODELS | str = "small",
        skip_evidences: bool = False,
        max_new_tokens: int = 1024,
        do_sample: bool = False,
        **kwargs,
    ):
        if torch is None:
            raise ImportError("torch is not installed")

        if transformers is None:
            raise ImportError("transformers is not installed")

        super().__init__(backend)
        self.model = self.maybe_map_model(model)
        self._pipeline = HuggingFaceScopeClassificationPipeline(
            self.model,
            skip_evidences=skip_evidences,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            **kwargs,
        )

    def _classify(
        self,
        conversation: ScopeClassificationInput,
        ai_service_description: str | AIServiceDescription,
        skip_evidences: bool | None = None,
    ) -> ScopeClassification:
        generated_text = self._pipeline(
            inputs=PipelineInputs(conversation, ai_service_description),
            **(
                {"skip_evidences": skip_evidences} if skip_evidences is not None else {}
            ),
        )[0]["generated_text"]

        try:
            parsed_obj = json.loads(generated_text)
        except json.JSONDecodeError:
            # TODO generation errors: handle potentially invalid JSON (retry?)
            raise ValueError(f"Failed to parse generated text: {generated_text}")

        try:
            validated_obj = ScopeClassification.model_validate(parsed_obj)
        except pydantic.ValidationError as e:
            # TODO generation errors: handle model validation failure (retry?)
            raise ValueError(f"Failed to validate generated text: {e}")

        return validated_obj

    def _batch_classify(
        self,
        conversations: list[ScopeClassificationInput],
        ai_service_description: str | AIServiceDescription | None = None,
        ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
        skip_evidences: bool | None = None,
    ) -> list[ScopeClassification]:
        if ai_service_descriptions is not None:
            pipeline_inputs = [
                PipelineInputs(c, ad)
                for c, ad in zip(conversations, ai_service_descriptions)
            ]
        elif ai_service_description is not None:
            pipeline_inputs = [
                PipelineInputs(c, ai_service_description) for c in conversations
            ]
        else:
            raise ValueError

        pipeline_outputs = self._pipeline(
            pipeline_inputs,
            **(
                {"skip_evidences": skip_evidences} if skip_evidences is not None else {}
            ),
        )

        results = []

        for pipeline_output in pipeline_outputs:
            # TODO generation errors: handle potentially invalid JSON (retry?)
            parsed_obj = json.loads(pipeline_output[0]["generated_text"])

            # TODO generation errors: handle model validation failure (retry?)
            results.append(
                ScopeClassification(
                    evidences=parsed_obj.get("evidences"),
                    scope_class=ScopeClass(parsed_obj["scope_class"]),
                )
            )

        return results
