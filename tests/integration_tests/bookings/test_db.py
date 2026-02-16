import pytest
from datetime import date

from src.schemas.bookings import BookingAdd


# ============ FIXTURES ============


@pytest.fixture(scope="function")
async def test_ids(db):
    """Fixture: returns (user_id, room_id, hotel_id) for tests."""
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    hotel_id = (await db.hotels.get_all(title=None, location=None, limit=1, offset=0))[0].id
    return user_id, room_id, hotel_id


@pytest.fixture(scope="function")
async def sample_booking(db, test_ids):
    """Fixture: creates and returns a booking for tests that need existing data."""
    user_id, room_id, hotel_id = test_ids

    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        hotel_id=hotel_id,
        check_in_date=date(2027, 6, 1),
        check_out_date=date(2027, 6, 5),
        price=2000,
    )

    created = await db.bookings.add(booking_data)
    await db.commit()
    return created


# ============ TESTS ============


async def test_create_booking(db, test_ids):
    """Test booking creation."""
    user_id, room_id, hotel_id = test_ids

    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        hotel_id=hotel_id,
        check_in_date=date(2027, 3, 1),
        check_out_date=date(2027, 3, 5),
        price=1500,
    )

    result = await db.bookings.add(booking_data)
    await db.commit()

    assert result.id is not None
    assert result.user_id == user_id
    assert result.price == 1500


async def test_read_booking(db, sample_booking):
    """Test reading booking by ID."""
    fetched = await db.bookings.get_one_or_none(id=sample_booking.id)

    assert fetched is not None
    assert fetched.id == sample_booking.id
    assert fetched.price == sample_booking.price


async def test_update_booking(db, sample_booking, test_ids):
    """Test updating booking."""
    user_id, room_id, hotel_id = test_ids

    update_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        hotel_id=hotel_id,
        check_in_date=date(2027, 7, 10),
        check_out_date=date(2027, 7, 15),
        price=5000,
    )

    await db.bookings.edit(update_data, id=sample_booking.id)
    await db.commit()

    updated = await db.bookings.get_one_or_none(id=sample_booking.id)

    assert updated.check_in_date == date(2027, 7, 10)
    assert updated.price == 5000


async def test_delete_booking(db, sample_booking):
    """Test deleting booking."""
    booking_id = sample_booking.id

    # Delete
    await db.bookings.delete(id=booking_id)
    await db.commit()

    # Verify deleted
    deleted = await db.bookings.get_one_or_none(id=booking_id)
    assert deleted is None
