async def test_get_hotels(ac):
    hotels = await ac.get("/hotels", params={"date_from": "2026-01-01", "date_to": "2026-10-10"})
    assert hotels.status_code == 200
    assert len(hotels.json()) > 0
