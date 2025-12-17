from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Response, status


from fastapi import APIRouter
from src.schemas.users import UserRequestAdd, UserAdd, UserLogin
from src.repositories.users import UsersRepository
from src.database import new_session
from src.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["authorization and authentication"])


@router.post("/register")
async def register_user(user_data: UserRequestAdd):
    hashed_password = AuthService().hash_password(user_data.password)
    new_user = UserAdd(
        **user_data.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
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
async def login(
    user_data: UserLogin,
    response: Response,
):
    async with new_session() as session:
        user = await UsersRepository(session).get_one_or_none(email=user_data.email)
        if not user or not AuthService().verify_password(
            user_data.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        access_token = AuthService().create_access_token(
            {"user_id": user.id, "username": user.username}
        )
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return {"access_token": access_token}
