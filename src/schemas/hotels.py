from pydantic import BaseModel, Field


class Hotel(BaseModel):
    title:        str = Field(..., description="Title of the hotel")
    location:     str = Field(..., description="Location of the hotel")


class HotelPatch(BaseModel):
    title:      str | None = Field(None, description="Title of the hotel")
    location:   str | None = Field(None, description="Location of the hotel")
