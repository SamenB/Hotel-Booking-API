from src.models.facilities import RoomFacilitiesOrm
from src.repositories.base import BaseRepository
from src.models.facilities import FacilitiesOrm
from src.repositories.mappers.mappers import FacilityMapper, FacilityRoomMapper
from sqlalchemy import select, delete, insert


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilityMapper


class RoomFacilitiesRepository(BaseRepository):
    model = RoomFacilitiesOrm
    mapper = FacilityRoomMapper

    async def set_room_facilities(self, room_id: int, facility_ids: list[int]):
        get_current_facilities_id_query = select(self.model.facility_id).where(
            self.model.room_id == room_id
        )
        result = await self.session.execute(get_current_facilities_id_query)
        current_facilities_id: list[int] = result.scalars().all()
        ids_to_delete = set(current_facilities_id) - set(facility_ids)
        ids_to_add = set(facility_ids) - set(current_facilities_id)

        if ids_to_delete:
            delete_stmt = delete(self.model).where(
                self.model.room_id == room_id,
                self.model.facility_id.in_(ids_to_delete),
            )
            await self.session.execute(delete_stmt)
        if ids_to_add:
            add_stmt = insert(self.model).values(
                [
                    {"room_id": room_id, "facility_id": facility_id}
                    for facility_id in ids_to_add
                ]
            )
            await self.session.execute(add_stmt)


    # async def set_room_facilities(self, room_id: int, facility_ids: list[int]):
    #     # 1. Fetch the room object along with its currently associated facilities
    #     # We use selectinload to eagerly load the relationship in an async-friendly way
    #     stmt = (
    #         select(RoomsOrm)
    #         .filter_by(id=room_id)
    #         .options(selectinload(RoomsOrm.facilities))
    #     )
    #     result = await self.session.execute(stmt)
    #     room = result.scalar_one()

    #     # 2. Fetch the Facility objects corresponding to the IDs we want to assign
    #     new_facilities_stmt = select(FacilitiesOrm).filter(FacilitiesOrm.id.in_(facility_ids))
    #     new_facilities = (await self.session.execute(new_facilities_stmt)).scalars().all()

    #     # 3. Synchronize the relationship by replacing the collection
    #     # We simply assign the new list to the relationship attribute
    #     room.facilities = new_facilities 
        
    #     # 4. SQLAlchemy's Unit of Work will automatically perform the "diff":
    #     # - Any facility removed from the list will be deleted from the 'room_facilities' table
    #     # - Any facility added to the list will be inserted into the 'room_facilities' table
    #     # All this happens automatically upon the next session flush or commit.