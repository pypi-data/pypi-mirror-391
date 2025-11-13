from gova_commons.enums import MessagePlatformType
from gova_commons.lib.models import MessageContext
from pydantic import BaseModel


class DiscordContext(BaseModel):
    """A replacement for discord.Message"""

    channel_id: int
    guild_id: int


class DiscordMessageContext(MessageContext):
    "Context object for discord"
    platform: MessagePlatformType = MessagePlatformType.DISCORD
    metadata: DiscordContext
