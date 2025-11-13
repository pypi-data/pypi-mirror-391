from enum import Enum
from typing import Literal, Union

from pydantic import Field

from gova_commons.lib.base.actions import BaseAction, BaseActionDefinition


class DiscordActionType(str, Enum):
    BAN = "ban"
    MUTE = "mute"
    KICK = "kick"


class BanAction(BaseAction):
    type: Literal[DiscordActionType.BAN] = DiscordActionType.BAN
    user_id: int


class BanActionDefinition(BaseActionDefinition):
    type: Literal[DiscordActionType.BAN] = DiscordActionType.BAN


class MuteAction(BaseAction):
    type: Literal[DiscordActionType.MUTE] = DiscordActionType.MUTE
    user_id: int
    duration: int = Field(
        ..., ge=0, description="Duration in milliseconds to mute the user."
    )


class MuteActionDefinition(BaseActionDefinition):
    type: Literal[DiscordActionType.MUTE] = DiscordActionType.MUTE
    duration: int | None = Field(
        None, ge=0, description="Duration in milliseconds to mute the user."
    )


class KickAction(BaseAction):
    type: Literal[DiscordActionType.KICK] = DiscordActionType.KICK
    user_id: int


class KickActionDefinition(BaseActionDefinition):
    type: Literal[DiscordActionType.KICK] = DiscordActionType.KICK


DiscordAction = Union[BanAction, MuteAction, KickAction]
DiscordActionDefinition = Union[
    MuteActionDefinition, BanActionDefinition, KickActionDefinition
]
