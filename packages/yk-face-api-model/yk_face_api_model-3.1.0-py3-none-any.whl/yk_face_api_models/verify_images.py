""" Verify Images Request """
from pydantic import BaseModel, Field


class VerifyImages(BaseModel):
    """ VerifyImages Model """
    first_image: str = Field(...,)
    second_image: str = Field(...,)
