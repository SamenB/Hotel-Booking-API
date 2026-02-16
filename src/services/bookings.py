from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from src.exeptions import (
    ObjectNotFoundException,
    AllRoomsAreBookedException,
    ObjectAlreadyExistsException,
    DatabaseException,
)
from src.services.base import BaseService
from src.schemas.bookings import BookingAddRequest, BookingAdd, BookingBulkRequest


class BookingService(BaseService):
    async def get_all_bookings(self):
        try:
            return await self.db.bookings.get_all()
        except SQLAlchemyError:
            raise DatabaseException

    async def get_my_bookings(self, user_id: int):
        try:
            return await self.db.bookings.get_filtered(user_id=user_id)
        except SQLAlchemyError:
            raise DatabaseException

    async def create_booking(self, booking_data: BookingAddRequest, user_id: int):
        try:
            booking = await self.db.bookings.create_booking(booking_data, user_id, self.db)
            await self.db.commit()
        except (ObjectNotFoundException, AllRoomsAreBookedException):
            raise
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Booking created: {}", booking)
        return booking

    async def create_bookings_bulk(self, bookings_data: list[BookingBulkRequest]):
        try:
            valid_user_ids = {u.id for u in await self.db.users.get_all()}
            valid_hotel_ids = {h.id for h in await self.db.hotels.get_filtered()}
            valid_room_ids = {r.id for r in await self.db.rooms.get_all()}

            valid = [
                BookingAdd(**b.model_dump())
                for b in bookings_data
                if b.user_id in valid_user_ids
                and b.hotel_id in valid_hotel_ids
                and b.room_id in valid_room_ids
            ]

            if valid:
                await self.db.bookings.add_bulk(valid)
                await self.db.commit()
        except ObjectAlreadyExistsException:
            raise
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException

        skipped = len(bookings_data) - len(valid)
        logger.info("Bulk bookings: inserted={}, skipped={}", len(valid), skipped)
        return {"inserted": len(valid), "skipped": skipped}

    async def get_bookings_timeline(self):
        """Get all bookings for timeline visualization."""
        try:
            return await self.db.bookings.get_all()
        except SQLAlchemyError:
            raise DatabaseException
