from src.schemas.hotels import HotelAdd


async def test_add_hotel(db):
    hotel_data = HotelAdd(title="Test Hotel", location="Test Hotel Location")
    await db.hotels.add(hotel_data)
    await db.commit()
