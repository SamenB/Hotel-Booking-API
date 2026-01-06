from src.repositories.mappers.base import DataMapper
from src.models.users import UsersOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.facilities import FacilitiesOrm, RoomFacilitiesOrm
from src.models.bookings import BookingsOrm
from src.schemas.hotels import Hotel
from src.schemas.users import User
from src.schemas.rooms import Room
from src.schemas.facilities import Facility, FacilityRoom
from src.schemas.bookings import Booking



class HotelMapper(DataMapper):
    db_model = HotelsOrm
    schema = Hotel

class UserMapper(DataMapper):
    db_model = UsersOrm
    schema = User

class RoomMapper(DataMapper):
    db_model = RoomsOrm
    schema = Room

class FacilityMapper(DataMapper):
    db_model = FacilitiesOrm
    schema = Facility

class FacilityRoomMapper(DataMapper):
    db_model = RoomFacilitiesOrm
    schema = FacilityRoom

class BookingMapper(DataMapper):
    db_model = BookingsOrm
    schema = Booking

