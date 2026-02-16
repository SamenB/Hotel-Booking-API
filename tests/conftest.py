from unittest.mock import patch

patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda func: func).start()


import pytest
from httpx import ASGITransport, AsyncClient
import json
from pathlib import Path
from datetime import datetime
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from src.main import app
from src.database import Base, engine_null_pool, new_session_null_pool
from src.models import *
from src.config import settings
from src.utils.db_manager import DBManager
from src.schemas.users import UserAdd
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.schemas.facilities import FacilityAdd, FacilityRoomAdd
from src.schemas.bookings import BookingAdd


MOCKS_DIR = Path(__file__).parent / "mocks"


def load_mock(filename: str) -> list[dict]:
    with open(MOCKS_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="function")
async def db():
    async with DBManager(session_factory=new_session_null_pool) as db:
        yield db


@pytest.fixture(scope="session", autouse=True)
async def check_test_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    # 1. Drop and create tables
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 2. Load mock data from JSON
    users_data = load_mock("users.json")
    hotels_data = load_mock("hotels.json")
    rooms_data = load_mock("rooms.json")
    facilities_data = load_mock("facilities.json")
    room_facilities_data = load_mock("room_facilities.json")
    bookings_data = load_mock("bookings.json")

    # 3. Convert dates in bookings (JSON has strings)
    for booking in bookings_data:
        booking["check_in_date"] = datetime.strptime(booking["check_in_date"], "%Y-%m-%d").date()
        booking["check_out_date"] = datetime.strptime(booking["check_out_date"], "%Y-%m-%d").date()

    # 4. Validate through Pydantic
    users = [UserAdd.model_validate(u) for u in users_data]
    hotels = [HotelAdd.model_validate(h) for h in hotels_data]
    rooms = [RoomAdd.model_validate(r) for r in rooms_data]
    facilities = [FacilityAdd.model_validate(f) for f in facilities_data]
    room_facilities = [FacilityRoomAdd.model_validate(rf) for rf in room_facilities_data]
    bookings = [BookingAdd.model_validate(b) for b in bookings_data]

    # 5. Insert using repositories
    async with DBManager(session_factory=new_session_null_pool) as db:
        await db.users.add_bulk(users)
        await db.hotels.add_bulk(hotels)
        await db.facilities.add_bulk(facilities)
        await db.rooms.add_bulk(rooms)
        await db.room_facilities.add_bulk(room_facilities)
        await db.bookings.add_bulk(bookings)
        await db.commit()


@pytest.fixture(scope="session")
async def ac():
    """Async HTTP client for testing API endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def register_user(ac, setup_database):
    response = await ac.post(
        url="/auth/register",
        json={"email": "qwerty@123.com", "password": "password", "username": "qwerty"},
    )
    assert response.status_code == 200


@pytest.fixture(scope="session")
async def authenticated_ac(register_user, ac):
    """Fixture: returns AsyncClient with auth cookie."""
    response = await ac.post(
        "/auth/login",
        json={
            "email": "qwerty@123.com",
            "password": "password",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies
    return ac


@pytest.fixture
async def delete_all_bookings(db):
    """Delete all bookings before test, restore clean state after."""
    await db.bookings.delete()
    await db.commit()


@pytest.fixture(scope="session", autouse=True)
async def init_cache(setup_database):
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")


# pytest -v -s
