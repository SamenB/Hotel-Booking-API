from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
import jwt

from fastapi import APIRouter
from src.schemas.users import UserRequestAdd, UserAdd, UserLogin
from src.repositories.users import UsersRepository
from src.database import new_session


router = APIRouter(prefix="/auth", tags=["authorization and authentication"])
password_hash = PasswordHash.recommended()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register")
async def register_user(user_data: UserRequestAdd):
    new_user = UserAdd(
        **user_data.model_dump(exclude={"password"}),
        hashed_password=password_hash.hash(user_data.password),
    )
    async with new_session() as session:
        try:
            await UsersRepository(session).add(new_user)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists",
            )
    return {"status": "OK"}


@router.post("/login")
async def login(user_data: UserLogin):
    async with new_session() as session:
        user = await UsersRepository(session).get_one_or_none(email=user_data.email)
        if not user or not password_hash.verify(
            user_data.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
