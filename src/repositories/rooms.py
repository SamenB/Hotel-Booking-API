from src.repositories.base import BaseRepository
from src.models.rooms import RoomsORM
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsORM
    schema = Room
