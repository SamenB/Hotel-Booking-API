from src.utils.db_manager import DBManager
from src.schemas.hotels import HotelAdd
from src.database import new_session




async def test_add_hotel():
    hotel_data = HotelAdd(
        title="Test Hotel",
        location="Test Hotel Location"
    )
    async with DBManager(session_factory=new_session) as db:
        await db.hotels.add(hotel_data)
        await db.commit()
    