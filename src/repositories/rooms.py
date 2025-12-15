from src.repositories.base import BaseRepository
from src.models.rooms import RoomOrm


class RoomsRepository(BaseRepository):
    model = RoomOrm
