""" Identify Image Request """
from typing import Optional
from pydantic import BaseModel, Field


class IdentifyImageRequest(BaseModel):
    """ IdentifyImageRequest Model """

    image: str = Field(description = "Query image to be identified in a specified gallery." )
    candidate_list_length: Optional[int] = Field(default=1, ge=1)
    minimum_score: Optional[float] = Field(default=-1, ge=-1)
    gallery_id: str
    liveness_check: Optional[bool] = Field(
        description="Check passive liveness in the query image.",
        default=False)
