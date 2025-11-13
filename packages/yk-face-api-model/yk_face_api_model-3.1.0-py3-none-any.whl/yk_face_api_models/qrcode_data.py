""" QRCodeData """
from typing import Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, ConfigDict


def get_default_expire_date() -> datetime:
    return datetime.now() + timedelta(days=5*365)


class QRCodeData(BaseModel):
    """ QRCodeData Model """
    template: str = Field(..., description="Biometric template as base64 string")
    version: Optional[str] = Field("v1", description="QRCode version")
    extra_fields: Optional[Dict] = Field(
        None, description="Additional data fields",
    )
    expire_date: Optional[datetime] = Field(
        default_factory=get_default_expire_date,
        description="QRcode expiration date")
    model_config = ConfigDict(title="The QRCode data model")
