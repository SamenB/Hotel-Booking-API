import pytest


async def test_add_booking(authenticated_ac):
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": 1,
            "check_in_date": "2026-02-01",
            "check_out_date": "2026-02-05",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert data["data"]["room_id"] == 1
    assert data["data"]["check_in_date"] == "2026-02-01"
    assert data["data"]["check_out_date"] == "2026-02-05"
    assert data["data"]["price"] > 0


async def test_booking_exceeds_room_quantity(authenticated_ac):
    """Room 2 (Presidential Suite) has quantity=1, so second booking should fail."""
    # First booking — should succeed
    response1 = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": 2,
            "check_in_date": "2028-08-01",
            "check_out_date": "2028-08-05",
        },
    )
    assert response1.status_code == 200

    # Second booking for SAME room with overlapping dates — should fail
    response2 = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": 2,
            "check_in_date": "2028-08-02",
            "check_out_date": "2028-08-04",
        },
    )
    assert response2.status_code == 409
    assert "All rooms are booked" in response2.json()["detail"]


@pytest.mark.parametrize(
    "booking_count, room_ids",
    [
        (1, [1]),
        (2, [1, 3]),
        (3, [1, 3, 7]),
    ],
)
async def test_create_and_get_my_bookings(
    authenticated_ac, delete_all_bookings, booking_count, room_ids
):
    """Create N bookings, then check GET /bookings/me returns exactly N."""
    # Create bookings
    for room_id in room_ids:
        response = await authenticated_ac.post(
            "/bookings",
            json={
                "room_id": room_id,
                "check_in_date": "2029-06-01",
                "check_out_date": "2029-06-05",
            },
        )
        assert response.status_code == 200

    # Check my bookings
    response = await authenticated_ac.get("/bookings/me")
    assert response.status_code == 200

    my_bookings = response.json()
    assert len(my_bookings) == booking_count

    booked_room_ids = [b["room_id"] for b in my_bookings]
    for room_id in room_ids:
        assert room_id in booked_room_ids
