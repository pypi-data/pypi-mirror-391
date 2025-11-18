from pydantic import BaseModel, Field


class SendingConfig(BaseModel):
    """Configuration parameters for the sender"""

    include_mention: bool = Field(
        default=False,
        description="Set to True if the created Note should mention the target",
    )
    include_cc: bool = Field(
        default=False,
        description="Set to True to ensure the activity and note contain cc",
    )
    public_value: str = Field(
        default="https://www.w3.org/ns/activitystreams#Public",
        description="The default value to use for public, see https://codeberg.org/funfedidev/python_fediverse_pasture/issues/41",
    )
