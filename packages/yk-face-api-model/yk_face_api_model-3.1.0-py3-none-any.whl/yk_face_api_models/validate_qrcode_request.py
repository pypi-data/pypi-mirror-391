""" Validate QRCode Request """
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ValidateQRCodeRequest(BaseModel):
    """ Validate QRCode Request Model """
    selfie_template: str = Field(..., description="Selfie biometric template as base64 string")
    qrcode: str = Field(...,description="QRCode string")
    is_decoded: Optional[bool] = Field(
        True,
        description="Set false if using qrcode image directly as the qrcode string")
    version: Optional[str] = Field("v1", description="QRCode version")
    model_config = ConfigDict(title="The Validate QRCode Request")

