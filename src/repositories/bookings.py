from src.repositories.base import BaseRepository
from src.models.bookings import BookingsOrm
from src.repositories.mappers.mappers import BookingMapper
from sqlalchemy import select, func
from datetime import date


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingMapper

    async def get_bookings_with_today_checkin(self):
        query = select(self.model).where(
            func.date(self.model.check_in_date) == date.today()
        )
        res = await self.session.execute(query)
        return [self.mapper.map_to_schema(model) for model in res.scalars().all()]