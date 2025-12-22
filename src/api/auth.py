from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Response, status
from fastapi import APIRouter

from src.schemas.users import UserRequestAdd, UserAdd, UserLogin
from src.services.auth import AuthService
from src.api.dependencies import UserDep
from src.api.dependencies import DBDep


router = APIRouter(prefix="/auth", tags=["authorization and authentication"])


@router.post("/register")
async def register_user(db: DBDep, user_data: UserRequestAdd):
    hashed_password = AuthService().hash_password(user_data.password)
    new_user = UserAdd(
        **user_data.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
    )
    try:
        await db.users.add(new_user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or username already exists",
        )
    return {"status": "OK"}


@router.post("/register/bulk")
async def register_users_bulk(db: DBDep, users_data: list[UserRequestAdd]):
    """
    Register multiple users at once (bulk insert).
    Single SQL INSERT statement.
    """
    users_to_add = [
        UserAdd(
            **user_data.model_dump(exclude={"password"}),
            hashed_password=AuthService().hash_password(user_data.password),
        )
        for user_data in users_data
    ]
    try:
        await db.users.add_bulk(users_to_add)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="One or more users already exist",
        )

    return {"status": "OK", "created": len(users_to_add)}


@router.post("/login")
async def login(
    db: DBDep,
    user_data: UserLogin,
    response: Response,
):
    user = await db.users.get_one_or_none(email=user_data.email)
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


@router.get("/me")
async def get_current_user(db: DBDep, user_id: UserDep):
    user = await db.users.get_one_or_none(id=user_id)
    return {"data": user}


@router.post("/logout")
async def logout(db: DBDep, response: Response):
    response.delete_cookie("access_token")
    await db.commit()
    return {"status": "OK"}
