""" Verify Request """
from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    """ VerifyRequest Model """
    first_template: str = Field(..., description="First Template")
    second_template: str = Field(..., description="Second Template")
