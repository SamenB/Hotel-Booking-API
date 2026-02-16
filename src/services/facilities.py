from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from src.exeptions import ObjectAlreadyExistsException, DatabaseException
from src.services.base import BaseService
from src.schemas.facilities import FacilityAdd


class FacilityService(BaseService):
    async def get_all_facilities(self):
        try:
            return await self.db.facilities.get_all()
        except SQLAlchemyError:
            raise DatabaseException

    async def create_facility(self, facility_data: FacilityAdd):
        try:
            facility = await self.db.facilities.add(facility_data)
            await self.db.commit()
        except ObjectAlreadyExistsException:
            raise
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseException
        logger.info("Facility created: {}", facility_data.title)
        return facility
