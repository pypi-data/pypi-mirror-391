import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scope_classifier import AsyncScopeClassifier
from scope_classifier.classifiers.vllm import VLLMAsyncApiScopeClassifier
from scope_classifier.modeling import (
    AIServiceDescription,
    ScopeClass,
    ScopeClassificationInput,
)

scope_classifier: VLLMAsyncApiScopeClassifier


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scope_classifier

    scope_classifier = AsyncScopeClassifier(  # type: ignore[invalid-assignment]
        backend="vllm-async-api",
        model=os.environ["SCOPE_CLASSIFIER_VLLM_MODEL"],
        skip_evidences=os.environ["SCOPE_CLASSIFIER_SKIP_EVIDENCES"] == "1",
        vllm_serving_url=os.environ["SCOPE_CLASSIFIER_VLLM_SERVING_URL"],
    )

    yield


app = FastAPI(
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScopeClassificationResponse(BaseModel):
    scope_class: ScopeClass
    evidences: list[str] | None
    time_taken: float
    model: str


@app.post(
    "/api/in/scope-classifier/classify", response_model=ScopeClassificationResponse
)
async def classify(
    conversation: ScopeClassificationInput,
    ai_service_description: str | AIServiceDescription,
    skip_evidences: bool | None = None,
) -> ScopeClassificationResponse:
    global scope_classifier

    start_time = time.time()
    result = await scope_classifier.classify(
        conversation, ai_service_description, skip_evidences
    )
    end_time = time.time()

    return ScopeClassificationResponse(
        scope_class=result.scope_class,
        evidences=result.evidences,
        time_taken=end_time - start_time,
        model=scope_classifier.model,
    )


@app.post(
    "/api/in/scope-classifier/batch-classify",
    response_model=list[ScopeClassificationResponse],
)
async def batch_classify(
    conversations: list[ScopeClassificationInput],
    ai_service_description: str | AIServiceDescription | None = None,
    ai_service_descriptions: list[str] | list[AIServiceDescription] | None = None,
    skip_evidences: bool | None = None,
) -> list[ScopeClassificationResponse]:
    global scope_classifier

    start_time = time.time()
    results = await scope_classifier.batch_classify(
        conversations,
        ai_service_description=ai_service_description,
        ai_service_descriptions=ai_service_descriptions,
        skip_evidences=skip_evidences,
    )
    end_time = time.time()

    return [
        ScopeClassificationResponse(
            scope_class=result.scope_class,
            evidences=result.evidences,
            time_taken=end_time - start_time,
            model=scope_classifier.model,
        )
        for result in results
    ]
