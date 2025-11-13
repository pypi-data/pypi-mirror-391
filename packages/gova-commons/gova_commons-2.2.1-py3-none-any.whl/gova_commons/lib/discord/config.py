from gova_commons.models import CustomBaseModel
from .actions import DiscordActionDefinition


class DiscordConfig(CustomBaseModel):
    guild_id: int
    allowed_channels: tuple[int, ...]
    allowed_actions: tuple[DiscordActionDefinition, ...]
