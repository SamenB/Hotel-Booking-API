from src.repositories.base import BaseRepository
from src.models.hotels import HotelsOrm
from sqlalchemy import select
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    schema = Hotel

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
        return [
            self.schema.model_validate(model, from_attributes=True)
            for model in result.scalars().all()
        ]
