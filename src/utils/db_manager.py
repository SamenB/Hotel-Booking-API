import asyncio                            
from sqlalchemy.exc import OperationalError  

from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository
from src.repositories.users import UsersRepository
from src.repositories.bookings import BookingsRepository
from src.repositories.facilities import FacilitiesRepository, RoomFacilitiesRepository




class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.hotels = HotelsRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.users = UsersRepository(self.session)
        self.bookings = BookingsRepository(self.session)
        self.facilities = FacilitiesRepository(self.session)
        self.room_facilities = RoomFacilitiesRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:  # Rollback только если была ошибка
            await self.session.rollback()
        await self.session.close()

    async def commit(self):
        '''
            session commit with deadlock exception handling
        '''
        for attempt in range(3):
            try:
                await self.session.commit()
                return
            except OperationalError as e:
                if "deadlock" in str(e).lower():
                    await self.session.rollback()
                    if attempt < 2:
                        await asyncio.sleep(0.1 * (attempt + 1))
                        continue
                raise
