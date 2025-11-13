""" Verify Image Request """
from typing import Optional
from pydantic import BaseModel, Field


class VerifyImageRequest(BaseModel):
    """ VerifyIdRequest Model """
    image: str = Field(description="Query image to verify against template enrolled in gallery.")
    template_id: str = Field(description="Template id used for registration.")
    gallery_id: Optional[str] = Field(None, description="Gallery id in which template_id is enrolled.")
    liveness_check: Optional[bool] = Field(
        description="Check passive liveness in the query image.",
        default=False)
