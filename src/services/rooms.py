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
from src.schemas.rooms import RoomAdd, RoomAddBulk, RoomPatch, RoomAddRequest, RoomPatchRequest
from src.schemas.facilities import FacilityRoomAdd


class RoomService(BaseService):
    async def get_room_by_id(self, hotel_id: int, room_id: int):
        room = await self.db.rooms.get_one(id=room_id, hotel_id=hotel_id)
        return room

    async def get_all_rooms(self, hotel_id: int, date_from: date, date_to: date):
        check_date_range(date_from, date_to)
        try:
            rooms = await self.db.rooms.get_filtered_by_time(
                hotel_id=hotel_id, date_from=date_from, date_to=date_to
            )
        except SQLAlchemyError:
            raise DatabaseException
        logger.info("Rooms retrieved: count={}", len(rooms))
        return rooms

    async def create_room(self, hotel_id: int, room_data: RoomAddRequest):
        # Verify hotel exists
        await self.db.hotels.get_one(id=hotel_id)

        try:
            room = await self.db.rooms.add(RoomAdd(**room_data.model_dump(), hotel_id=hotel_id))
            room_facilities = [
                FacilityRoomAdd(room_id=room.id, facility_id=facility_id)
                for facility_id in room_data.facilities
            ]
            await self.db.room_facilities.add_bulk(room_facilities)
            await self.db.commit()
        except ObjectAlreadyExistsException:
            raise
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Room created: id={}, hotel_id={}", room.id, hotel_id)
        return room

    async def update_room(self, hotel_id: int, room_id: int, room_data: RoomAddRequest):
        # Verify room exists
        await self.db.rooms.get_one(id=room_id)

        try:
            await self.db.rooms.edit(RoomAdd(**room_data.model_dump(), hotel_id=hotel_id), id=room_id)
            await self.db.room_facilities.set_room_facilities(room_id, room_data.facilities)
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Room updated: id={}", room_id)

    async def update_room_partially(self, room_id: int, room_data: RoomPatchRequest):
        room_data_dict = room_data.model_dump(exclude_unset=True)
        # Verify room exists and get hotel_id
        room = await self.db.rooms.get_one(id=room_id)

        try:
            _room_data = RoomPatch(**room_data_dict, hotel_id=room.hotel_id)
            await self.db.rooms.edit(_room_data, exclude_unset=True, id=room_id)
            if "facilities" in room_data_dict:
                await self.db.room_facilities.set_room_facilities(room_id, room_data.facilities)
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Room partially updated: id={}", room_id)

    async def delete_room(self, room_id: int):
        # Verify room exists
        await self.db.rooms.get_one(id=room_id)

        try:
            await self.db.rooms.delete(id=room_id)
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Room deleted: id={}", room_id)

    async def create_rooms_bulk(self, rooms_data: list[RoomAddBulk]):
        # Verify all hotel_ids exist
        hotel_ids = set(room.hotel_id for room in rooms_data)
        for hotel_id in hotel_ids:
            await self.db.hotels.get_one(id=hotel_id)

        try:
            rooms_to_add = [RoomAdd(**room.model_dump()) for room in rooms_data]
            await self.db.rooms.add_bulk(rooms_to_add)
            await self.db.commit()
        except ObjectAlreadyExistsException:
            raise
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Bulk rooms created: count={}", len(rooms_to_add))
        return len(rooms_to_add)
