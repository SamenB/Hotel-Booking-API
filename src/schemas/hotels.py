from pydantic import BaseModel, Field


class HotelAdd(BaseModel):
    title: str = Field(..., description="Title of the hotel")
    location: str = Field(..., description="Location of the hotel")


class Hotel(HotelAdd):
    id: int = Field(..., description="ID of the hotel")
    images: list[str] | None = Field(None, description="List of image URLs")


class HotelPatch(BaseModel):
    title: str | None = Field(None, description="Title of the hotel")
    location: str | None = Field(None, description="Location of the hotel")
