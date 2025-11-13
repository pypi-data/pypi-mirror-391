from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from gova_commons.enums import MessagePlatformType
from gova_commons.lib.base.actions import BaseAction
from gova_commons.models import CustomBaseModel


T = TypeVar("T", bound=BaseAction)


class MessageContext(CustomBaseModel):
    platform: MessagePlatformType
    platform_author_id: str
    platform_message_id: str
    content: str
    metadata: Any


class TopicEvaluation(BaseModel):
    topic: str
    topic_score: float


class MessageEvaluation(CustomBaseModel, Generic[T]):
    evaluation_score: float
    topic_evaluations: list[TopicEvaluation]
    action: T | None
