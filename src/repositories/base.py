from fastapi.exceptions import HTTPException
from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel


class BaseRepository:
    """
    Base repository class for working with custom sessions and models
    """

    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add(self, data: BaseModel | list[BaseModel]):
        if isinstance(data, list):
            data_to_insert = [sample.model_dump() for sample in data]
        else:
            data_to_insert = data.model_dump()
        add_stmt = insert(self.model).values(data_to_insert).returning(self.model.id)
        # raw_sql = add_stmt.compile(dialect=postgresql.dialect(),
        #                                   compile_kwargs={"literal_binds": True})
        # print(raw_sql)
        result = await self.session.execute(add_stmt)
        return result.scalars().all()

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by):
        edit_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(data.model_dump(exclude_unset=exclude_unset))
        )
        result = await self.session.execute(edit_stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="hotel not found")
        return result

    async def delete(self, **filter_by):
        delete_stmt = delete(self.model).filter_by(**filter_by)
        result = await self.session.execute(delete_stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="hotel not found")
        return result
