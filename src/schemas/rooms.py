from pydantic import BaseModel, Field


class RoomAddRequest(BaseModel):
    title: str = Field(..., description="Title of the room")
    description: str | None = Field(None, description="Description of the room")
    price: int = Field(..., description="Price of the room")
    quantity: int = Field(..., description="Quantity of the room")


class RoomAdd(RoomAddRequest):
    hotel_id: int = Field(..., description="ID of the hotel")


class Room(RoomAdd):
    id: int = Field(..., description="ID of the room")


class RoomPatch(BaseModel):
    title: str | None = Field(None, description="Title of the room")
    description: str | None = Field(None, description="Description of the room")
    price: int | None = Field(None, description="Price of the room")
    quantity: int | None = Field(None, description="Quantity of the room")
    hotel_id: int | None = Field(None, description="ID of the hotel")
