from src.repositories.base import BaseRepository
from src.models.bookings import BookingsOrm
from src.repositories.mappers.mappers import BookingMapper
from src.repositories.utils import room_ids_for_booking
from src.schemas.bookings import BookingAddRequest, BookingAdd
from sqlalchemy import select, func
from datetime import date


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingMapper

    async def create_booking(self, booking_data: BookingAddRequest, user_id: int, db):
        """Validate availability and create booking."""
        # 1. Check if room exists
        room = await db.rooms.get_one_or_none(id=booking_data.room_id)
        if not room:
            return None, "Room not found"

        # 2. Check room availability for the selected dates
        available_rooms = await db.rooms.get_filtered_by_time(
            hotel_id=room.hotel_id,
            date_from=booking_data.check_in_date,
            date_to=booking_data.check_out_date,
        )
        available_ids = [r.id for r in available_rooms]
        if booking_data.room_id not in available_ids:
            return None, "No available rooms for the selected dates"

        # 3. Create booking
        booking = await self.add(
            BookingAdd(
                **booking_data.model_dump(),
                hotel_id=room.hotel_id,
                user_id=user_id,
                price=room.price,
            )
        )
        return booking, None

    async def get_bookings_with_today_checkin(self):
        query = select(self.model).where(
            func.date(self.model.check_in_date) == date.today()
        )
        res = await self.session.execute(query)
        return [self.mapper.map_to_schema(model) for model in res.scalars().all()]