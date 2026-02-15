from datetime import date
from fastapi.exceptions import HTTPException  # noqa: F401
from fastapi import APIRouter, Body, Query
from src.schemas.rooms import (
    RoomAddRequest,
    RoomAdd,
    RoomAddBulk,
    RoomPatchRequest,
    RoomPatch,
)
from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityRoomAdd


router = APIRouter(prefix="/hotels/{hotel_id}/rooms", tags=["Rooms"])
bulk_router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/{room_id}")
async def get_room_by_id(db: DBDep, hotel_id: int, room_id: int):
    room = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.get("")
async def get_all_rooms(
    db: DBDep,
    hotel_id: int,
    date_from: date = Query(examples=["2025-01-01"]),
    date_to: date = Query(examples=["2025-01-05"]),
):
    rooms = await db.rooms.get_filtered_by_time(
        hotel_id=hotel_id, date_from=date_from, date_to=date_to
    )
    return rooms


@router.post("")
async def create_room(
    db: DBDep,
    hotel_id: int,
    room_data: RoomAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Luxury",
                "value": {
                    "title": "Luxury Suite",
                    "description": "Sea view",
                    "price": 15000,
                    "quantity": 5,
                    "facilities": [1, 2],
                },
            },
            "2": {
                "summary": "Standard",
                "value": {
                    "title": "Standard Room",
                    "description": None,
                    "price": 5000,
                    "quantity": 20,
                    "facilities": [1, 2],
                },
            },
        }
    ),
):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    room = await db.rooms.add(RoomAdd(**room_data.model_dump(), hotel_id=hotel_id))
    room_facilities = [
        FacilityRoomAdd(room_id=room.id, facility_id=facility_id)
        for facility_id in room_data.facilities
    ]
    await db.room_facilities.add_bulk(room_facilities)
    await db.commit()
    return {"status": "OK", "data": room}


@router.put("/{room_id}")
async def update_room(db: DBDep, hotel_id: int, room_id: int, room_data: RoomAddRequest):
    room = await db.rooms.get_one_or_none(id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    await db.rooms.edit(RoomAdd(**room_data.model_dump(), hotel_id=hotel_id), id=room_id)
    await db.room_facilities.set_room_facilities(room_id, room_data.facilities)
    await db.commit()
    return {"status": "OK"}


@router.patch(
    "/{room_id}",
    summary="Update room partially",
    description="Update any fields that are provided",
)
async def update_room_partially(db: DBDep, room_id: int, room_data: RoomPatchRequest):
    room_data_dict = room_data.model_dump(exclude_unset=True)
    room = await db.rooms.get_one_or_none(id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    _room_data = RoomPatch(**room_data_dict, hotel_id=room.hotel_id)
    await db.rooms.edit(_room_data, exclude_unset=True, id=room_id)
    if "facilities" in room_data_dict:
        await db.room_facilities.set_room_facilities(room_id, room_data.facilities)
    await db.commit()
    return {"status": "OK"}


@router.delete("/{room_id}")
async def delete_room(db: DBDep, room_id: int):
    room = await db.rooms.get_one_or_none(id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    await db.rooms.delete(id=room_id)
    await db.commit()
    return {"status": "OK"}


@bulk_router.post("/bulk")
async def create_rooms_bulk(db: DBDep, rooms_data: list[RoomAddBulk]):
    """
    Create multiple rooms at once (bulk insert).
    hotel_id is passed in body for each room.
    """
    # Проверяем что все hotel_id существуют
    hotel_ids = set(room.hotel_id for room in rooms_data)
    for hotel_id in hotel_ids:
        hotel = await db.hotels.get_one_or_none(id=hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail=f"Hotel with id={hotel_id} not found")

    # Конвертируем в RoomAdd (схема та же, просто для ясности)
    rooms_to_add = [RoomAdd(**room.model_dump()) for room in rooms_data]

    await db.rooms.add_bulk(rooms_to_add)
    await db.commit()

    return {"status": "OK", "created": len(rooms_to_add)}
