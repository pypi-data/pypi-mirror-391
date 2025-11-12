from enum import Enum


class PricingTierType(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class MessagePlatformType(str, Enum):
    DISCORD = "discord"


class ModeratorStatus(str, Enum):
    OFFLINE = "offline"
    PENDING = "pending"
    ONLINE = "online"


class ActionStatus(str, Enum):
    FAILED = "failed"
    SUCCESS = "success"
    DECLINED = "declined"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"


class CoreEventType(str, Enum):
    MODERATOR_EVENT = "moderator_event"


class ModeratorEventType(str, Enum):
    START = "start"
    ALIVE = "alive"
    STOP = "stop"
    DEAD = "dead"
    FAILED = "failed"
    HEARTBEAT = "heartbeat"
    ACTION_PERFORMED = "action"
    ACTION_APPROVED = 'action_approved'
    EVALUATION_CREATED = "evaluation"
    ERROR = "error"
    WARNING = "warning"


class LogSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
