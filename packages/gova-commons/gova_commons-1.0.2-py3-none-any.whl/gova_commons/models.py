from datetime import datetime
from enum import Enum
from json import loads
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

from gova_commons.enums import MessagePlatformType


class CustomBaseModel(BaseModel):
    model_config = {
        "json_encoders": {
            UUID: str,
            datetime: lambda dt: dt.isoformat(),
            Enum: lambda e: e.value,
        }
    }

    def to_serialisable_dict(self) -> dict:
        return loads(self.model_dump_json())


class Action(CustomBaseModel):
    type: Enum
    requires_approval: bool
    reason: str = Field(description="Filled by the system and not the agent.")


class ActionDefinition(CustomBaseModel):
    """
    The client facing model(s) which allow prefilling
    parameters. Used in the platforms config for defining
    the allowed actions.
    """

    type: Enum
    requires_approval: bool


class MessageContext(CustomBaseModel):
    platform: MessagePlatformType
    platform_author_id: str
    platform_message_id: str
    content: str
    metadata: Any


class TopicEvaluation(BaseModel):
    topic: str
    topic_score: float


T = TypeVar("T", bound=Action)


class MessageEvaluation(CustomBaseModel, Generic[T]):
    evaluation_score: float
    topic_evaluations: list[TopicEvaluation]
    action: T | None
