""" Identify Request """
from typing import Optional
from pydantic import BaseModel, Field


class IdentifyRequest(BaseModel):
    """ IdentifyRequest Model """

    template: str = Field(..., )
    candidate_list_length: Optional[int] = Field(default=1, ge=1)
    minimum_score: Optional[float] = Field(default=-1, ge=-1)
    gallery_id: str
