from fastapi import Query, Depends
from pydantic import BaseModel
from typing import Annotated
from fastapi import Request
from src.services.auth import AuthService
from fastapi import HTTPException
from src.utils.db_manager import DBManager
from src.database import new_session
from src.exeptions import TokenExpiredException, InvalidTokenException


class PaginationParams(BaseModel):
    page: Annotated[int, Query(1, ge=1, description="Page number")]
    per_page: Annotated[
        int | None, Query(None, ge=1, lt=500, description="Number of hotels per page")
    ]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request):
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token


def get_current_user_id(token: str = Depends(get_token)):
    try:
        data = AuthService().decode_access_token(token)
    except TokenExpiredException:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenException:
        raise HTTPException(status_code=401, detail="Invalid token")
    return data["user_id"]


UserDep = Annotated[int, Depends(get_current_user_id)]


async def get_db():
    async with DBManager(session_factory=new_session) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
