""" Template """
from typing import Optional
from pydantic import BaseModel, Field


class Template(BaseModel):
    """ Template """
    template: str
    duplicate_check: Optional[bool] = Field(
        description="Template request. When inserting in gallery also enables deduplicate check.",
        default=False,
    )
