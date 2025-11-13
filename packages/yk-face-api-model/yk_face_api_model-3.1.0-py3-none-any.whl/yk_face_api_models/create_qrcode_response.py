""" Create QRcode Response """
from pydantic import BaseModel, Field, ConfigDict


class CreateQRCodeResponse(BaseModel):
    """ Create QRCode Response Model """
    qrcode: str = Field(..., description="QRCode image as base64 string")
    model_config = ConfigDict(title="The Create QRCode Response")
