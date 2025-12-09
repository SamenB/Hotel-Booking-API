from pydantic import BaseModel, Field


class Hotel(BaseModel):
    name:        str = Field(..., description="Name of the hotel")
    description: str = Field(..., description="Description of the hotel")
    price:       int = Field(..., description="Price per night for the hotel")


class HotelPatch(BaseModel):
    name:        str | None = Field(None, description="Name of the hotel")
    description: str | None = Field(None, description="Description of the hotel")
    price:       int | None = Field(None, description="Price per night for the hotel")
