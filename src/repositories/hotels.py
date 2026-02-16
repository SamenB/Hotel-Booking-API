from src.repositories.base import BaseRepository
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from sqlalchemy import select
from src.repositories.mappers.mappers import HotelMapper
from src.repositories.utils import room_ids_for_booking
from datetime import date


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelMapper

    async def get_all(
        self,
        title: str | None,
        location: str | None,
        limit: int,
        offset: int,
    ):
        query = select(self.model)
        if title:
            query = query.filter(self.model.title.ilike(f"%{title}%"))
        if location:
            query = query.filter(self.model.location.ilike(f"%{location}%"))
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [self.mapper.map_to_schema(model) for model in result.scalars().all()]

    async def get_filtered_by_time(
        self,
        date_from: date,
        date_to: date,
        available: bool = True,
        limit: int = 10,
        offset: int = 0,
        title: str | None = None,
        location: str | None = None,
    ):
        rooms_ids_to_get = room_ids_for_booking(date_from, date_to)
        hotels_ids_with_rooms = select(RoomsOrm.hotel_id)
        if available:
            hotels_ids_with_rooms = hotels_ids_with_rooms.where(RoomsOrm.id.in_(rooms_ids_to_get))
        else:
            hotels_ids_with_rooms = hotels_ids_with_rooms.where(
                RoomsOrm.id.notin_(rooms_ids_to_get)
            )

        query = select(self.model).where(HotelsOrm.id.in_(hotels_ids_with_rooms))
        if title:
            query = query.filter(self.model.title.ilike(f"%{title}%"))
        if location:
            query = query.filter(self.model.location.ilike(f"%{location}%"))
        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        return [self.mapper.map_to_schema(model) for model in result.scalars().all()]
