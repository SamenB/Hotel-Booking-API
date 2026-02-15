from datetime import date
from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
from src.repositories.utils import room_ids_for_booking
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from src.repositories.mappers.mappers import RoomMapper
from src.schemas.rooms import RoomWithFacilities


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomMapper
    """
    with rooms_count as (
        select room_id, count(*) as rooms_booked from bookings 
        where check_in_date  <= :date_to
        and check_out_date >= :date_from
        group by room_id
    ),
    available_rooms as(
        select rooms.id as room_id, quantity - coalesce(rooms_booked, 0) as rooms_available from rooms
        left join rooms_count on rooms.id = rooms_count.room_id 

    )
    select * from available_rooms
    where rooms_available > 0 and room_id in (
        select id from rooms where hotel_id = {hotel_id}
    )
    """

    async def get_filtered_by_time(self, hotel_id: int, date_from: date, date_to: date):
        rooms_ids_to_get = room_ids_for_booking(date_from=date_from, date_to=date_to, hotel_id=hotel_id)

        query = (
            select(self.model)
            .options(joinedload(self.model.facilities))
            .filter(self.model.id.in_(rooms_ids_to_get))
        )
        result = await self.session.execute(query)
        return [RoomWithFacilities.model_validate(model, from_attributes=True) for model in result.unique().scalars().all()]


    async def get_one_or_none(self, **filter_by):
        query = select(self.model).options(joinedload(self.model.facilities)).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.unique().scalars().one_or_none()
        if model is None:
            return None
        return RoomWithFacilities.model_validate(model, from_attributes=True)