from datetime import date
from fastapi.exceptions import HTTPException  # noqa: F401
from fastapi import APIRouter, Body, Query
from src.schemas.rooms import (
    RoomAddRequest,
    RoomAddBulk,
    RoomPatchRequest,
)
from src.api.dependencies import DBDep
from src.exeptions import (
    ObjectNotFoundException,
    ObjectAlreadyExistsException,
    InvalidDateRangeException,
    DatabaseException,
)
from src.services.rooms import RoomService
from loguru import logger


router = APIRouter(prefix="/hotels/{hotel_id}/rooms", tags=["Rooms"])
bulk_router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/{room_id}")
async def get_room_by_id(db: DBDep, hotel_id: int, room_id: int):
    try:
        room = await RoomService(db).get_room_by_id(hotel_id, room_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.get("")
async def get_all_rooms(
    db: DBDep,
    hotel_id: int,
    date_from: date = Query(examples=["2025-01-01"]),
    date_to: date = Query(examples=["2025-01-05"]),
):
    try:
        rooms = await RoomService(db).get_all_rooms(hotel_id, date_from, date_to)
    except InvalidDateRangeException:
        raise HTTPException(status_code=422, detail="date_to must be after date_from")
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
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
    try:
        room = await RoomService(db).create_room(hotel_id, room_data)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Hotel not found")
    except ObjectAlreadyExistsException:
        raise HTTPException(status_code=409, detail="Room already exists")
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK", "data": room}


@router.put("/{room_id}")
async def update_room(db: DBDep, hotel_id: int, room_id: int, room_data: RoomAddRequest):
    try:
        await RoomService(db).update_room(hotel_id, room_id, room_data)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Room not found")
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK"}


@router.patch(
    "/{room_id}",
    summary="Update room partially",
    description="Update any fields that are provided",
)
async def update_room_partially(db: DBDep, room_id: int, room_data: RoomPatchRequest):
    try:
        await RoomService(db).update_room_partially(room_id, room_data)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Room not found")
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK"}


@router.delete("/{room_id}")
async def delete_room(db: DBDep, room_id: int):
    try:
        await RoomService(db).delete_room(room_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Room not found")
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK"}


@bulk_router.post("/bulk")
async def create_rooms_bulk(db: DBDep, rooms_data: list[RoomAddBulk]):
    """
    Create multiple rooms at once (bulk insert).
    hotel_id is passed in body for each room.
    """
    try:
        count = await RoomService(db).create_rooms_bulk(rooms_data)
    except ObjectNotFoundException as ex:
        raise HTTPException(status_code=404, detail=str(ex.detail))
    except ObjectAlreadyExistsException:
        raise HTTPException(status_code=409, detail="One or more rooms already exist")
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK", "created": count}
