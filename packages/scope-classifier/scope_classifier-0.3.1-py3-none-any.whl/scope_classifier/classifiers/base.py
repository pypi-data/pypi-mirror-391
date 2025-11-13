from __future__ import annotations

import logging
from typing import Literal

from pydantic import ValidationError

from ..modeling import (
    AIServiceDescription,
    ScopeClassification,
    ScopeClassificationInput,
    ScopeClassificationInputTypeAdapter,
)

MODELS = Literal["small"]

MODEL_MAPPING = {
    "small": "principled-intelligence/scope-classifier-Qwen3-1.7B-v0.4",
}


class BaseScopeClassifier:
    _registry: dict[str, type[ScopeClassifier | AsyncScopeClassifier]] = {}

    @classmethod
    def register_classifier(cls, backend: str):
        """Class decorator for registering a backend."""

        def decorator(subclass: type[BaseScopeClassifier]) -> type[BaseScopeClassifier]:
            cls._registry[backend] = subclass
            return subclass

        return decorator

    @classmethod
    def maybe_map_model(cls, model: MODELS | str) -> str:
        if model in MODEL_MAPPING:
            logging.warning(
                f"Detected simplified model name, using {MODEL_MAPPING[model]}"
            )
            return MODEL_MAPPING[model]
        return model

    def __new__(
        cls,
        backend: str = "hf",
        *args,
        **kwargs,
    ):
        if cls is not ScopeClassifier and cls is not AsyncScopeClassifier:
            # if called on subclass, behave normally
            return super().__new__(cls)

        try:
            subclass = cls._registry[backend]
        except KeyError:
            raise ValueError(
                f"Unknown backend '{backend}'. Available: {list(cls._registry)}"
            )

        return super().__new__(subclass)

    def __init__(
        self,
        backend: str,
        **kwargs,
    ):
        self.backend = backend

    def _validate_conversation(
        self, conversation: str | dict | list[dict]
    ) -> ScopeClassificationInput:
        try:
            return ScopeClassificationInputTypeAdapter.validate_python(conversation)
        except ValidationError as e:
            logging.error("Invalid input format for conversation")
            raise e from None

    def _validate_conversations(
        self, conversations: list[str] | list[dict] | list[list[dict]]
    ) -> list[ScopeClassificationInput]:
        validated_conversations = []
        for c in conversations:
            try:
                validated_conversations.append(self._validate_conversation(c))
            except ValidationError as e:
                logging.error("Invalid input format for conversation")
                raise e from None
        return validated_conversations

    def _validate_ai_service_description_input(
        self,
        conversations: list[ScopeClassificationInput],
        ai_service_description: str | AIServiceDescription,
        ai_service_descriptions: list[str] | list[AIServiceDescription],
    ):
        if bool(ai_service_description is not None) == bool(
            ai_service_descriptions is not None
        ):
            if ai_service_description is not None:
                raise ValueError(
                    "Only one between [ai_service_description, ai_service_descriptions] must be provided"
                )
            else:
                raise ValueError(
                    "Either ai_service_description or ai_service_descriptions must be provided"
                )

        if ai_service_descriptions is not None and len(conversations) != len(
            ai_service_descriptions
        ):
            raise ValueError(
                "The number of conversations and ai_service_descriptions must be the same"
            )


class ScopeClassifier(BaseScopeClassifier):
    def classify(
        self,
        conversation: str | dict | list[dict],
        ai_service_description: str | AIServiceDescription,
        skip_evidences: bool | None = None,
    ) -> ScopeClassification:
        conversation = self._validate_conversation(conversation)
        return self._classify(conversation, ai_service_description, skip_evidences)

    def _classify(
        self,
        conversation: ScopeClassificationInput,
        ai_service_description: str | AIServiceDescription,
        skip_evidences: bool | None = None,
    ) -> ScopeClassification:
        raise NotImplementedError

    def batch_classify(
        self,
        conversations: list[str] | list[dict] | list[list[dict]],
        ai_service_description: str | AIServiceDescription | None = None,
        ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
        skip_evidences: bool | None = None,
    ) -> list[ScopeClassification]:
        if len(conversations) == 0:
            return []

        validated_conversations = self._validate_conversations(conversations)
        self._validate_ai_service_description_input(
            validated_conversations, ai_service_description, ai_service_descriptions
        )

        return self._batch_classify(
            validated_conversations,
            ai_service_description,
            ai_service_descriptions,
            skip_evidences,
        )

    def _batch_classify(
        self,
        conversations: list[ScopeClassificationInput],
        ai_service_description: str | AIServiceDescription | None = None,
        ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
        skip_evidences: bool | None = None,
    ) -> list[ScopeClassification]:
        raise NotImplementedError


class AsyncScopeClassifier(BaseScopeClassifier):
    async def classify(
        self,
        conversation: str | dict | list[dict],
        ai_service_description: str | AIServiceDescription,
        skip_evidences: bool | None = None,
    ) -> ScopeClassification:
        conversation = self._validate_conversation(conversation)
        return await self._classify(
            conversation, ai_service_description, skip_evidences
        )

    async def _classify(
        self,
        conversation: ScopeClassificationInput,
        ai_service_description: str | AIServiceDescription,
        skip_evidences: bool | None = None,
    ) -> ScopeClassification:
        raise NotImplementedError

    async def batch_classify(
        self,
        conversations: list[str] | list[dict] | list[list[dict]],
        ai_service_description: str | AIServiceDescription | None = None,
        ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
        skip_evidences: bool | None = None,
    ) -> list[ScopeClassification]:
        if len(conversations) == 0:
            return []

        validated_conversations = self._validate_conversations(conversations)
        self._validate_ai_service_description_input(
            validated_conversations, ai_service_description, ai_service_descriptions
        )

        return await self._batch_classify(
            validated_conversations,
            ai_service_description,
            ai_service_descriptions,
            skip_evidences,
        )

    async def _batch_classify(
        self,
        conversations: list[ScopeClassificationInput],
        ai_service_description: str | AIServiceDescription | None = None,
        ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
        skip_evidences: bool | None = None,
    ) -> list[ScopeClassification]:
        raise NotImplementedError
