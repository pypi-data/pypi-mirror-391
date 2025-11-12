from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, TypeAdapter


class ScopeClass(str, Enum):
    DIRECTLY_SUPPORTED = "Directly Supported"
    POTENTIALLY_SUPPORTED = "Potentially Supported"
    OUT_OF_SCOPE = "Out of Scope"
    RESTRICTED = "Restricted"
    CHIT_CHAT = "Chit Chat"

    @property
    def description(self) -> str:
        return _SCOPE_DESCRIPTIONS[self]

    @property
    def examples(self) -> list[str] | None:
        return _EXAMPLES.get(self)

    @classmethod
    def get_classes_manifest(cls) -> str:
        manifest = ""
        for cc in cls:
            manifest += f"**Name**: {cc.value}\n**Description**: {cc.description}\n"
            if cc.examples:
                manifest += (
                    "**Examples**:\n"
                    + "\n".join(map(lambda x: f"* {x}", cc.examples))
                    + "\n\n"
                )
            else:
                manifest += "\n"
        return manifest


_SCOPE_DESCRIPTIONS = {
    ScopeClass.DIRECTLY_SUPPORTED: "The user's query can be definitively handled by the AI Service given the functionalities, knowledge scope, and capabilities described in the AI Service Description.",
    ScopeClass.POTENTIALLY_SUPPORTED: "The user's query can be plausibly handled by the AI Service given the functionalities, knowledge scope, and capabilities described in the AI Service Description. The request is a reasonable extension or interpretation of the service's capabilities that might be within scope.",
    ScopeClass.OUT_OF_SCOPE: "The user's query is outside the AI Service's role and functionalities. It's incompatible with the service's documented purpose.",
    ScopeClass.RESTRICTED: "The user's query cannot be handled by the AI Service due to either behavioral restrictions (content/advice the service must refuse to provide) or service limitations (technical constraints, access restrictions, or knowledge scope limitations).",
    ScopeClass.CHIT_CHAT: "The user's query is a casual or social interaction that does not pertain to the AI Service's functionalities, knowledge scope, or operational capabilities.",
}


_EXAMPLES = {
    ScopeClass.RESTRICTED: [
        "Do not provide personalized financial advice. → User: Should I invest my savings in Bitcoin?",
        "The AI service does not have access to real-time data. → User: What's the current stock price of Apple?",
        "AI service cannot access external databases. → User: Look up my account balance in the system.",
    ],
}


class ScopeClassification(BaseModel):
    evidences: list[str] | None = Field(
        description="Excerpts quoted directly from the AI Service Description that are relevant to understanding whether and how the AI Service can handle the LAST USER MESSAGE.",
        default=None,
    )
    scope_class: ScopeClass = Field(
        description="The classification assigned to the LAST USER MESSAGE based on the evidence extracted from the AI Service Description."
    )


class AIServiceDescription(BaseModel):
    identity_role: str = Field(
        description="Identity, role and objectives of the AI Service. Gives a general idea of what the service is about."
    )
    context: str = Field(
        description="Context in which the AI Service operates. The company, the sector, the users, the location, etc."
    )
    functionalities: str = Field(
        description="Functionalities provided by the AI Service"
    )
    knowledge_scope: str = Field(
        description="Scope of knowledge and expertise of the AI Service"
    )
    conduct_guidelines: str = Field(
        description="Conduct guidelines and principles followed by the AI Service"
    )
    constraints: str = Field(
        description="Constraints and limitations of the AI Service"
    )
    fallback: str = Field(
        description="Fallback mechanisms and strategies employed by the AI Service when it cannot fulfill a request"
    )
    website_url: str | None = Field(
        description="The URL of the AI Service website", default=None
    )


class ConversationUserMessage(BaseModel):
    role: Literal["user"]
    content: str


class ConversationMessage(BaseModel):
    role: str
    content: str


ScopeClassificationInput = str | ConversationUserMessage | list[ConversationMessage]

ScopeClassificationInputTypeAdapter = TypeAdapter(ScopeClassificationInput)
