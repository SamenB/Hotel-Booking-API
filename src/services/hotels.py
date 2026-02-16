from datetime import date

from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from src.exeptions import (
    check_date_range,
    ObjectNotFoundException,
    ObjectAlreadyExistsException,
    DatabaseException,
)
from src.services.base import BaseService
from src.schemas.hotels import HotelAdd, HotelPatch
from src.services.images import ImageService




class HotelService(BaseService):
    async def get_all_hotels(
        self,
        date_from: date,
        date_to: date,
        available: bool,
        title: str | None,
        location: str | None,
        per_page: int,
        offset: int,
    ):
        check_date_range(date_from, date_to)
        try:
            hotels = await self.db.hotels.get_filtered_by_time(
                date_from=date_from,
                date_to=date_to,
                available=available,
                title=title,
                location=location,
                limit=per_page,
                offset=offset,
            )
        except SQLAlchemyError:
            raise DatabaseException
        return hotels


    async def get_hotel_by_id(self, hotel_id: int):
        hotel = await self.db.hotels.get_one(id=hotel_id)
        if not hotel:
            raise ObjectNotFoundException("Hotel not found")
        return hotel

    async def create_hotel(self, hotel_data: HotelAdd | list[HotelAdd]):
        try:
            await self.db.hotels.add(hotel_data)
            await self.db.commit()
        except ObjectAlreadyExistsException:
            raise
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Hotel created: {}", hotel_data)

    async def update_hotel(self, hotel_id: int, hotel_data: HotelAdd):
        try:
            await self.db.hotels.edit(hotel_data, id=hotel_id)
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Hotel updated: id={}", hotel_id)

    async def update_hotel_partially(self, hotel_id: int, hotel_data: HotelPatch):
        try:
            await self.db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Hotel partially updated: id={}", hotel_id)

    async def delete_hotel(self, hotel_id: int):
        try:
            await self.db.hotels.delete(id=hotel_id)
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Hotel deleted: id={}", hotel_id)

    async def get_hotel_images(self, hotel_id: int):
        hotel = await self.db.hotels.get_one_or_none(id=hotel_id)
        if not hotel:
            raise ObjectNotFoundException("Hotel not found")
        return hotel.images or []

    @staticmethod
    def upload_hotel_image(hotel_id: int, file):
        ImageService.save_and_process_hotel_image(hotel_id, file)
        logger.info("Image uploaded for hotel_id={}, filename={}", hotel_id, file.filename)