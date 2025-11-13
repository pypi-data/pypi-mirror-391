""" Process Request """
from typing import List, Set, Optional
from pydantic import BaseModel, Field
from .process_request_config import ProcessRequestConfig  # noqa: F401,E501
from .processing_enum import ProcessingEnum


class ProcessRequest(BaseModel):
    """ ProcessRequest """
    image: str = Field(...)
    processings: Optional[Set[ProcessingEnum]] = Field(
        description="Requested biometric processings.",
        default={ProcessingEnum.detect, ProcessingEnum.analyze, ProcessingEnum.templify},
    )
    configuration: Optional[List[ProcessRequestConfig]] = Field(
        description="Extensible configurations for biometric processing.",
        default=[]
    )
