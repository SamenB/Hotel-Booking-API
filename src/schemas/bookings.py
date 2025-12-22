from pydantic import BaseModel, Field
from datetime import date


class BookingAddRequest(BaseModel):
    room_id: int = Field(..., description="ID of the room")
    check_in_date: date = Field(..., description="Check in date")
    check_out_date: date = Field(..., description="Check out date")


class BookingAdd(BookingAddRequest):
    hotel_id: int = Field(..., description="ID of the hotel")
    user_id: int = Field(..., description="ID of the user")
    price: int = Field(..., description="Price of the booking")


class Booking(BookingAdd):
    id: int = Field(..., description="ID of the booking")


class BookingBulkRequest(BaseModel):
    """Schema for bulk booking with all fields"""

    user_id: int
    hotel_id: int
    room_id: int
    check_in_date: date
    check_out_date: date
    price: int
