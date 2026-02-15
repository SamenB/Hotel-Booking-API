from fastapi.exceptions import HTTPException  # noqa: F401
from fastapi import Query, APIRouter, Body
from fastapi import UploadFile, File
from datetime import date

from src.schemas.hotels import HotelAdd, HotelPatch
from src.api.dependencies import PaginationDep
from src.api.dependencies import DBDep
from src.services.images import ImageService


router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("/{hotel_id}")
async def get_hotel_by_id(hotel_id: int, db: DBDep):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel


@router.get("")
async def get_hotels(
    db: DBDep,
    pagination: PaginationDep,
    date_from: date = Query(examples="2026-01-01"),
    date_to: date = Query(examples="2026-01-05"),
    available: bool = Query(True, description="Hotels with available rooms or without"),
    title: str | None = Query(None, description="Hotel title"),
    location: str | None = Query(None, description="Hotel location"),
):
    per_page = pagination.per_page or 10
    offset = (pagination.page - 1) * per_page
    hotels = await db.hotels.get_filtered_by_time(
        date_from=date_from,
        date_to=date_to,
        available=available,
        title=title,
        location=location,
        limit=per_page,
        offset=offset,
    )
    return hotels


@router.post("")
async def create_hotel(
    db: DBDep,
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
    await db.hotels.add(hotel_data)
    await db.commit()
    return {"status": "OK"}


@router.put("/{hotel_id}")
async def update_hotel(db: DBDep, hotel_id: int, hotel_data: HotelAdd):
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.patch(
    "/{hotel_id}",
    summary="Update hotel partially",
    description="Update any fields that are provided",
)
async def update_hotel_partially(db: DBDep, hotel_id: int, hotel_data: HotelPatch):
    await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(db: DBDep, hotel_id: int):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.post("/{hotel_id}/images")
async def upload_hotel_image(hotel_id: int, file: UploadFile = File(...)):
    ImageService.save_and_process_hotel_image(hotel_id, file)
    return {"status": "OK", "message": "Image processing started"}


@router.get("/{hotel_id}/images")
async def get_hotel_images(hotel_id: int, db: DBDep):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"images": hotel.images or []}
