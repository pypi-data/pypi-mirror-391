""" Process Request Configuration """
from typing import Union, Optional

from pydantic import BaseModel, Field


class ProcessRequestConfig(BaseModel):
    """ ProcessRequestConfig Model """
    name: str = Field(description="Configuration name")
    value: Optional[Union[float, str]] = Field(None, description="Configuration value for numbers and strings.")
    bvalue: Optional[bool] = Field(None, description="Configuration value for booleans.")
