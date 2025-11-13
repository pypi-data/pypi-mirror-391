import asyncio
from typing import Literal

import aiohttp
import requests

from ..modeling import (
    AIServiceDescription,
    ScopeClassification,
    ScopeClassificationInput,
    ScopeClassificationInputTypeAdapter,
)
from .base import AsyncScopeClassifier, ScopeClassifier


def _build_request_data(
    conversation: ScopeClassificationInput,
    skip_evidences: bool,
    ai_service_description: str | AIServiceDescription,
) -> dict:
    return {
        "conversation": ScopeClassificationInputTypeAdapter.dump_python(conversation),
        "ai_service_description": ai_service_description.model_dump()
        if isinstance(ai_service_description, AIServiceDescription)
        else ai_service_description,
        "skip_evidences": skip_evidences,
    }


def _build_batch_request_data(
    conversations: list[ScopeClassificationInput],
    skip_evidences: bool,
    ai_service_description: str | AIServiceDescription | None = None,
    ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
) -> dict:
    return {
        "conversations": [
            ScopeClassificationInputTypeAdapter.dump_python(conversation)
            for conversation in conversations
        ],
        **(
            (
                {"ai_service_description": ai_service_description.model_dump()}
                if isinstance(ai_service_description, AIServiceDescription)
                else {"ai_service_description": ai_service_description}
            )
            if ai_service_description is not None
            else {}
        ),
        **(
            {
                "ai_service_descriptions": [
                    (ad.model_dump() if isinstance(ad, AIServiceDescription) else ad)
                    for ad in ai_service_descriptions
                ]
            }
            if ai_service_descriptions is not None
            else {}
        ),
        "skip_evidences": skip_evidences,
    }


@ScopeClassifier.register_classifier("api")
class APIScopeClassifier(ScopeClassifier):
    def __init__(
        self,
        backend: Literal["api"] = "api",
        api_url: str = "http://localhost:8000",
        custom_headers: dict[str, str] = {},
        skip_evidences: bool = False,
    ):
        super().__init__(backend)
        self.skip_evidences = skip_evidences
        self.api_url = api_url
        self.custom_headers = custom_headers

    def _classify(
        self,
        conversation: ScopeClassificationInput,
        ai_service_description: str | AIServiceDescription,
        skip_evidences: bool | None = None,
    ) -> ScopeClassification:
        response = requests.post(
            f"{self.api_url}/api/in/scope-classifier/classify",
            json=_build_request_data(
                conversation,
                skip_evidences if skip_evidences is not None else self.skip_evidences,
                ai_service_description,
            ),
            headers={**self.custom_headers, "Content-Type": "application/json"},
        )
        response.raise_for_status()

        response_data = response.json()
        return ScopeClassification(
            scope_class=response_data["scope_class"],
            evidences=response_data["evidences"],
        )

    def _batch_classify(
        self,
        conversations: list[ScopeClassificationInput],
        ai_service_description: str | AIServiceDescription | None = None,
        ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
        skip_evidences: bool | None = None,
    ) -> list[ScopeClassification]:
        response = requests.post(
            f"{self.api_url}/api/in/scope-classifier/batch-classify",
            json=_build_batch_request_data(
                conversations,
                skip_evidences if skip_evidences is not None else self.skip_evidences,
                ai_service_description,
                ai_service_descriptions,
            ),
            headers={**self.custom_headers, "Content-Type": "application/json"},
        )
        response.raise_for_status()

        response_data = response.json()
        return [
            ScopeClassification(
                scope_class=result["scope_class"],
                evidences=result["evidences"],
            )
            for result in response_data
        ]


@AsyncScopeClassifier.register_classifier("async-api")
class AsyncAPIScopeClassifier(AsyncScopeClassifier):
    def __init__(
        self,
        backend: Literal["async-api"] = "async-api",
        api_url: str = "http://localhost:8000",
        custom_headers: dict[str, str] = {},
        skip_evidences: bool = False,
    ):
        super().__init__(backend)
        self.skip_evidences = skip_evidences
        self.api_url = api_url
        self.custom_headers = custom_headers

    async def _classify(
        self,
        conversation: ScopeClassificationInput,
        ai_service_description: str | AIServiceDescription,
        skip_evidences: bool | None = None,
    ) -> ScopeClassification:
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"{self.api_url}/api/in/scope-classifier/classify",
                json=_build_request_data(
                    conversation,
                    skip_evidences
                    if skip_evidences is not None
                    else self.skip_evidences,
                    ai_service_description,
                ),
                headers={**self.custom_headers, "Content-Type": "application/json"},
            )
            response.raise_for_status()
            response_data = await response.json()

        return ScopeClassification(
            scope_class=response_data["scope_class"],
            evidences=response_data["evidences"],
        )

    async def _batch_classify(
        self,
        conversations: list[ScopeClassificationInput],
        ai_service_description: str | AIServiceDescription | None = None,
        ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
        skip_evidences: bool | None = None,
    ) -> list[ScopeClassification]:
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"{self.api_url}/api/in/scope-classifier/batch-classify",
                json=_build_batch_request_data(
                    conversations,
                    skip_evidences
                    if skip_evidences is not None
                    else self.skip_evidences,
                    ai_service_description,
                    ai_service_descriptions,
                ),
                headers={**self.custom_headers, "Content-Type": "application/json"},
            )
            response.raise_for_status()
            response_data = await response.json()

        return [
            ScopeClassification(
                scope_class=result["scope_class"],
                evidences=result["evidences"],
            )
            for result in response_data
        ]
