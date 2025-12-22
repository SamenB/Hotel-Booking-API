from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel


class BaseRepository:
    """
    Base repository class for working with custom sessions and models
    """

    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(
        self, *filter, limit: int = 10, offset: int = 0, **filter_by
    ):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [
            self.schema.model_validate(model, from_attributes=True)
            for model in result.scalars().all()
        ]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered(**kwargs)

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.schema.model_validate(model, from_attributes=True)

    async def add(self, data: BaseModel | list[BaseModel]):
        if isinstance(data, list):
            data_to_insert = [sample.model_dump() for sample in data]
        else:
            data_to_insert = data.model_dump()
        add_stmt = insert(self.model).values(data_to_insert).returning(self.model)
        result = await self.session.execute(add_stmt)
        model = result.scalars().one()
        return self.schema.model_validate(model, from_attributes=True)

    async def edit(
        self, data: BaseModel, exclude_unset: bool = False, **filter_by
    ) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)

    async def add_bulk(self, data: list[BaseModel]) -> None:
        """
        Bulk insert multiple records in a single SQL statement.
        More efficient than inserting one by one.
        """
        data_to_insert = [item.model_dump() for item in data]
        add_stmt = insert(self.model).values(data_to_insert)
        await self.session.execute(add_stmt)
