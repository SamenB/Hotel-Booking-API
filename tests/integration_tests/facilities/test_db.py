from src.schemas.facilities import FacilityAdd

async def test_add_facilities(db):
    facility = await db.facilities.add(FacilityAdd(title="Test Facility"))
    await db.commit()
    assert facility.id is not None
    assert facility.title == "Test Facility"



async def test_get_facilities(db):
    facilities = await db.facilities.get_all()
    assert len(facilities) > 0