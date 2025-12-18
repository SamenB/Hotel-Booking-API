from fastapi.exceptions import HTTPException  # noqa: F401
from fastapi import Query, APIRouter, Body
from src.schemas.rooms import RoomAddRequest, RoomAdd
from src.api.dependencies import PaginationDep
from src.database import new_session
from src.repositories.rooms import RoomsRepository
from src.repositories.hotels import HotelsRepository


router = APIRouter(prefix="/hotels/{hotel_id}/rooms", tags=["Rooms"])


@router.get("/{room_id}")
async def get_room_by_id(hotel_id: int, room_id: int):
    async with new_session() as session:
        room = await RoomsRepository(session).get_one_or_none(
            id=room_id, hotel_id=hotel_id
        )
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room


@router.get("")
async def get_all_rooms(hotel_id: int):
    async with new_session() as session:
        rooms = await RoomsRepository(session).get_all(hotel_id=hotel_id)
        return rooms


@router.post("")
async def create_room(
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
                },
            },
            "2": {
                "summary": "Standard",
                "value": {
                    "title": "Standard Room",
                    "description": None,
                    "price": 5000,
                    "quantity": 20,
                },
            },
        }
    ),
):
    async with new_session() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id=hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        room = await RoomsRepository(session).add(
            RoomAdd(**room_data.model_dump(), hotel_id=hotel_id)
        )
        await session.commit()
        return {"status": "OK", "data": room}


@router.put("/{room_id}")
async def update_room(hotel_id: int, room_id: int, room_data: RoomAddRequest):
    async with new_session() as session:
        room = await RoomsRepository(session).get_one_or_none(id=room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        await RoomsRepository(session).edit(
            RoomAdd(**room_data.model_dump(), hotel_id=hotel_id), id=room_id
        )
        await session.commit()
        return {"status": "OK"}


@router.patch(
    "/{room_id}",
    summary="Update room partially",
    description="Update any fields that are provided",
)
async def update_room_partially(room_id: int, room_data: RoomAddRequest):
    async with new_session() as session:
        room = await RoomsRepository(session).get_one_or_none(id=room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        await RoomsRepository(session).edit(room_data, exclude_unset=True, id=room_id)
        await session.commit()
        return {"status": "OK"}


@router.delete("/{room_id}")
async def delete_room(room_id: int):
    async with new_session() as session:
        await RoomsRepository(session).delete(id=room_id)
        await session.commit()
        return {"status": "OK"}
