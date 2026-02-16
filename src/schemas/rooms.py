from pydantic import BaseModel, Field
from src.schemas.facilities import Facility


class RoomAddRequest(BaseModel):
    title: str = Field(..., description="Title of the room")
    description: str | None = Field(None, description="Description of the room")
    price: int = Field(..., description="Price of the room")
    quantity: int = Field(..., description="Quantity of the room")
    facilities: list[int] = Field([], description="List of facility IDs")


class RoomAdd(BaseModel):
    title: str = Field(..., description="Title of the room")
    description: str | None = Field(None, description="Description of the room")
    price: int = Field(..., description="Price of the room")
    quantity: int = Field(..., description="Quantity of the room")
    hotel_id: int = Field(..., description="ID of the hotel")


class Room(RoomAdd):
    id: int = Field(..., description="ID of the room")


class RoomWithFacilities(Room):
    facilities: list[Facility]


class RoomPatchRequest(BaseModel):
    title: str | None = Field(None, description="Title of the room")
    description: str | None = Field(None, description="Description of the room")
    price: int | None = Field(None, description="Price of the room")
    quantity: int | None = Field(None, description="Quantity of the room")
    facilities: list[int] = Field([], description="List of facility IDs")


class RoomPatch(BaseModel):
    hotel_id: int | None = Field(None, description="ID of the hotel")
    title: str | None = Field(None, description="Title of the room")
    description: str | None = Field(None, description="Description of the room")
    price: int | None = Field(None, description="Price of the room")
    quantity: int | None = Field(None, description="Quantity of the room")


class RoomAddBulk(BaseModel):
    """Schema for bulk room creation with hotel_id in body"""

    hotel_id: int = Field(..., description="ID of the hotel")
    title: str = Field(..., description="Title of the room")
    description: str | None = Field(None, description="Description of the room")
    price: int = Field(..., description="Price of the room")
    quantity: int = Field(..., description="Quantity of the room")
