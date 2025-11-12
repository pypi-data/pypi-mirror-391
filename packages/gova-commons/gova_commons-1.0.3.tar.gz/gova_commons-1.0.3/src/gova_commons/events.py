from typing import Any, Generic, Literal, TypeVar
from uuid import UUID, uuid4

from pydantic import Field

from gova_commons.enums import (
    ActionStatus,
    CoreEventType,
    MessagePlatformType,
    ModeratorEventType,
)
from gova_commons.models import (
    CustomBaseModel,
    Action,
    MessageContext,
    MessageEvaluation,
)
from gova_commons.utils.db import get_datetime


A = TypeVar("A", bound=Action)
M = TypeVar("M", bound=MessageContext)
C = TypeVar("C")


class CoreEvent(CustomBaseModel):
    """Generic system event."""

    type: CoreEventType
    data: Any
    id: UUID = Field(default_factory=uuid4)
    timestamp: int = Field(default_factory=lambda: int(get_datetime().timestamp()))


# Moderator Events


class ModeratorEvent(CustomBaseModel):
    """Base deployment event."""

    type: ModeratorEventType
    moderator_id: UUID


class StartModeratorEvent(ModeratorEvent, Generic[C]):
    """Deployment start request."""

    type: ModeratorEventType = ModeratorEventType.START
    moderator_id: UUID
    platform: MessagePlatformType
    conf: C


class StopModeratorEvent(ModeratorEvent):
    """Deployment stop request."""

    type: ModeratorEventType = ModeratorEventType.STOP
    reason: str | None = None


class DeadModeratorEvent(ModeratorEvent):
    """Deployment stopped."""

    type: ModeratorEventType = ModeratorEventType.DEAD
    reason: str | None = None


class HeartbeatModeratorEvent(ModeratorEvent):
    type: ModeratorEventType = ModeratorEventType.HEARTBEAT
    role: Literal["moderator", "server"]
    timestamp: int


class ActionPerformedModeratorEvent(ModeratorEvent, Generic[A, M]):
    """Deployment action event."""

    type: ModeratorEventType = ModeratorEventType.ACTION_PERFORMED
    action_type: Any  # Enum
    params: A
    status: ActionStatus
    context: M
    message_id: UUID


class ActionApprovedModeratorEvent(ModeratorEvent):
    "Emitted when an action has been approved and is to be processed"

    type: ModeratorEventType = ModeratorEventType.ACTION_APPROVED
    action: A
    context: M


class EvaluationCreatedModeratorEvent(ModeratorEvent, Generic[A, M]):
    """Message evaluation result."""

    type: ModeratorEventType = ModeratorEventType.EVALUATION_CREATED
    message_id: UUID
    evaluation: MessageEvaluation[A]
    context: M


class ErrorModeratorEvent(ModeratorEvent):
    type: ModeratorEventType = ModeratorEventType.ERROR
    stack_trace: str | None = None
