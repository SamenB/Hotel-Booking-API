from src.models.rooms import RoomsOrm
from src.models.bookings import BookingsOrm
from sqlalchemy import select, func
from datetime import date


def room_ids_for_booking(date_from: date, date_to: date, hotel_id: int | None = None):
    rooms_count = (
        select(BookingsOrm.room_id, func.count("*").label("rooms_booked"))
        .where(
            BookingsOrm.check_in_date <= date_to,
            BookingsOrm.check_out_date >= date_from,
        )
        .group_by(BookingsOrm.room_id)
        .cte("rooms_count")
    )

    # CTE 2: available_rooms - calculate available room quantity
    rooms_available = (RoomsOrm.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label(
        "rooms_available"
    )
    available_rooms = (
        select(RoomsOrm.id.label("room_id"), rooms_available)
        .select_from(RoomsOrm)
        .outerjoin(rooms_count, RoomsOrm.id == rooms_count.c.room_id)
        .cte("available_rooms")
    )

    # Final query: select rooms with rooms_available > 0 and add filter by hotel_id
    rooms_ids_for_hotel = select(RoomsOrm.id)
    if hotel_id:
        rooms_ids_for_hotel = rooms_ids_for_hotel.where(RoomsOrm.hotel_id == hotel_id)
    # rooms_ids_for_hotel = rooms_ids_for_hotel.subquery()

    rooms_ids_to_get = (
        select(available_rooms.c.room_id)
        .select_from(available_rooms)
        .where(
            available_rooms.c.rooms_available > 0,
            available_rooms.c.room_id.in_(rooms_ids_for_hotel),
        )
    )

    # print(
    #     rooms_ids_to_get.compile(bind=engine, compile_kwargs={"literal_binds": True})
    # )
    return rooms_ids_to_get
