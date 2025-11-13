""" Gallery Response """
from typing import List
from pydantic import BaseModel


class GalleryResponse(BaseModel):
    """ GalleryResponse Model """
    enrolled_ids: List[str] = []
