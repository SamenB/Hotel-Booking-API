from fastapi.exceptions import HTTPException  # noqa: F401
from fastapi import Query, APIRouter, Body
from src.schemas.hotels import HotelAdd, HotelPatch
from src.api.dependencies import PaginationDep
from src.database import new_session
from src.repositories.hotels import HotelsRepository


router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("/{hotel_id}")
async def get_hotel_by_id(hotel_id: int):
    async with new_session() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id=hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        return hotel


@router.get("")
async def get_hotels(
    pagination: PaginationDep,
    title: str | None = Query(None, description="Title of the hotel"),
    location: str | None = Query(None, description="Location of the hotel"),
):
    per_page = pagination.per_page or 10
    async with new_session() as session:
        hotels = await HotelsRepository(session).get_all(
            title=title,
            location=location,
            limit=per_page,
            offset=(pagination.page - 1) * per_page,
        )
        return hotels


@router.post("")
async def create_hotel(
    hotel_data: HotelAdd | list[HotelAdd] = Body(
        openapi_examples={
            "1": {
                "summary": "Hotel 3",
                "value": {"title": "Hotel 3", "location": "Hotel 3 description"},
            },
            "2": {
                "summary": "Hotel 4",
                "value": {"title": "Hotel 4", "location": "Hotel 4 description"},
            },
        }
    ),
):
    async with new_session() as session:
        await HotelsRepository(session).add(hotel_data)
        await session.commit()
        return {"status": "OK"}


@router.put("/{hotel_id}")
async def update_hotel(hotel_id: int, hotel_data: HotelAdd):
    async with new_session() as session:
        await HotelsRepository(session).edit(hotel_data, id=hotel_id)
        await session.commit()
        return {"status": "OK"}


@router.patch(
    "/{hotel_id}",
    summary="Update hotel partially",
    description="Update any fields that are provided",
)
async def update_hotel_partially(hotel_id: int, hotel_data: HotelPatch):
    async with new_session() as session:
        await HotelsRepository(session).edit(
            hotel_data, exclude_unset=True, id=hotel_id
        )
        await session.commit()
        return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int):
    async with new_session() as session:
        await HotelsRepository(session).delete(id=hotel_id)
        await session.commit()
        return {"status": "OK"}
