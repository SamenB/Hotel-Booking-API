async def test_add_facilities(ac):
    facilities = await ac.post(
        "/facilities",
        json={
            "title": "Test Facility 2",
        },
    )
    assert facilities.status_code == 200
    assert len(facilities.json()) > 0


async def test_get_facilities(ac):
    facilities = await ac.get("/facilities")
    assert facilities.status_code == 200
    assert len(facilities.json()) > 0
