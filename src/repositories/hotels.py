from src.repositories.base import BaseRepository
from src.models.hotels import HotelsOrm
from sqlalchemy import select


class HotelsRepository(BaseRepository):
    model = HotelsOrm

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
        hotels = result.scalars().all()
        return hotels
