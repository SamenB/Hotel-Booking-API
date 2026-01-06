from pydantic import BaseModel, Field


class FacilityAdd(BaseModel):
    title: str = Field(..., description="Title of the facility")


class Facility(FacilityAdd):
    id: int = Field(..., description="ID of the facility")


class FacilityRoomAdd(BaseModel):
    facility_id: int = Field(..., description="ID of the facility")
    room_id: int = Field(..., description="ID of the room")


class FacilityRoom(FacilityRoomAdd):
    id: int = Field(..., description="ID of the facility room")
