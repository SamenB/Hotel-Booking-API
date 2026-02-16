from fastapi.exceptions import HTTPException  # noqa: F401
from fastapi import Query, APIRouter, Body
from fastapi import UploadFile, File
from datetime import date
from loguru import logger

from src.schemas.hotels import HotelAdd, HotelPatch
from src.api.dependencies import PaginationDep
from src.api.dependencies import DBDep
from src.exeptions import (
    ObjectNotFoundException,
    ObjectAlreadyExistsException,
    InvalidDateRangeException,
    DatabaseException,
)
from src.services.hotels import HotelService


router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("/{hotel_id}")
async def get_hotel_by_id(hotel_id: int, db: DBDep):
    try:
        hotel = await HotelService(db).get_hotel_by_id(hotel_id)
    except ObjectNotFoundException:
        logger.warning("Hotel with id={} not found", hotel_id)
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

@router.get("")
async def get_hotels(
    db: DBDep,
    pagination: PaginationDep,
    date_from: date = Query(examples=["2026-01-01"]),
    date_to: date = Query(examples=["2026-01-05"]),
    available: bool = Query(True, description="Hotels with available rooms or without"),
    title: str | None = Query(None, description="Hotel title"),
    location: str | None = Query(None, description="Hotel location"),
):
    per_page = pagination.per_page or 10
    offset = (pagination.page - 1) * per_page
    try:
        hotels = await HotelService(db).get_all_hotels(
            date_from=date_from,
            date_to=date_to,
            available=available,
            title=title,
            location=location,
            per_page=per_page,
            offset=offset,
        )
    except DatabaseException:
        logger.error("Database error occurred")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except InvalidDateRangeException:
        raise HTTPException(status_code=422, detail=InvalidDateRangeException.detail)
    return hotels


@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd | list[HotelAdd] = Body(  # type: ignore[arg-type]
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
    try:
        await HotelService(db).create_hotel(hotel_data)
    except ObjectAlreadyExistsException:
        raise HTTPException(status_code=409, detail="Hotel already exists")
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK"}


@router.put("/{hotel_id}")
async def update_hotel(db: DBDep, hotel_id: int, hotel_data: HotelAdd):
    try:
        await HotelService(db).update_hotel(hotel_id, hotel_data)
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK"}


@router.patch(
    "/{hotel_id}",
    summary="Update hotel partially",
    description="Update any fields that are provided",
)
async def update_hotel_partially(db: DBDep, hotel_id: int, hotel_data: HotelPatch):
    try:
        await HotelService(db).update_hotel_partially(hotel_id, hotel_data)
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(db: DBDep, hotel_id: int):
    try:
        await HotelService(db).delete_hotel(hotel_id)
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK"}


@router.post("/{hotel_id}/images")
async def upload_hotel_image(hotel_id: int, file: UploadFile = File(...)):
    HotelService.upload_hotel_image(hotel_id, file)
    return {"status": "OK", "message": "Image processing started"}


@router.get("/{hotel_id}/images")
async def get_hotel_images(hotel_id: int, db: DBDep):
    try:
        images = await HotelService(db).get_hotel_images(hotel_id)
    except ObjectNotFoundException:
        logger.warning("Hotel with id={} not found", hotel_id)
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"images": images}
