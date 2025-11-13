""" Verify Id Request """
from typing import Optional
from pydantic import BaseModel, Field


class VerifyIdRequest(BaseModel):
    """ VerifyIdRequest Model """
    template: str = Field(...)
    template_id: str = Field(...)
    gallery_id: Optional[str] = None
