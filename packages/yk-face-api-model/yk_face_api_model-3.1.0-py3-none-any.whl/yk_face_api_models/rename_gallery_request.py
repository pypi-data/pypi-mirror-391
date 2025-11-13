""" Rename Gallery Request """
from pydantic import BaseModel, Field


class RenameGalleryRequest(BaseModel):
    """ RenameGalleryRequest Model """

    current_gallery_name: str = Field(...)
    new_gallery_name: str = Field(...)
