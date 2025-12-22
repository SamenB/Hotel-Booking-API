from datetime import date
from src.repositories.base import BaseRepository
from src.models.rooms import RoomsORM
from src.schemas.rooms import Room
from src.repositories.utils import room_ids_for_booking


class RoomsRepository(BaseRepository):
    model = RoomsORM
    schema = Room
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
        rooms_ids_to_get = room_ids_for_booking(hotel_id, date_from, date_to)
        rooms = await self.get_filtered(RoomsORM.id.in_(rooms_ids_to_get))
        return rooms
