from enum import Enum

from pydantic import Field

from gova_commons.models import CustomBaseModel


class BaseAction(CustomBaseModel):
    "Base model for all actions performed by a moderator"

    type: Enum
    requires_approval: bool
    reason: str = Field(description="Filled by the system and not the agent.")


class BaseActionDefinition(CustomBaseModel):
    """
    The client facing model(s) which allow prefilling
    parameters. Used in the platforms config for defining
    the allowed actions.
    """

    type: Enum
    requires_approval: bool
