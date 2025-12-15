from fastapi import Query, Depends
from pydantic import BaseModel
from typing import Annotated

class PaginationParams(BaseModel):
    page:     Annotated[int, Query(1, ge=1, description="Page number")]
    per_page: Annotated[int | None, Query(None, ge=1, lt=100, description="Number of hotels per page")]


PaginationDep = Annotated[PaginationParams, Depends()]
