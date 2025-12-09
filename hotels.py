from fastapi import Body, Query, APIRouter
from schemas.hotels import Hotel, HotelPatch


router = APIRouter(prefix="/hotels", tags=["Hotels"])


hotels = [
    {
        "id": 1,
        "name": "Hotel 1",
        "description": "Hotel 1 description",
        "price": 100,
    },
    {
        "id": 2,
        "name": "Hotel 2",
        "description": "Hotel 2 description",
        "price": 200,
    }
]

@router.get("")
def get_hotels(
                id: int | None = Query(None, description="ID of the hotel"), # None -defoult, ... - required  
                name: str | None = Query(None, description="Name of the hotel")
    ):
    looking_for_hotel = []
    for hotel in hotels:
        id_match = (id is None) or hotel["id"] == id
        name_match = (name is None) or hotel["name"] == name
        if id_match and name_match:
            looking_for_hotel.append(hotel)
    return looking_for_hotel



@router.post("")
def create_hotel(
    hotel_data: Hotel = Body(openapi_examples={
        "1": {"summary": "Hotel 3", "value": {"name": "Hotel 3", "description": "Hotel 3 description", "price": 1000}}, 
        "2": {"summary": "Hotel 4", "value": {"name": "Hotel 4", "description": "Hotel 4 description", "price": 2000}}
    })
):
    hotel_id = len(hotels) + 1
    hotel = {"id": hotel_id, "name": hotel_data.name, "description": hotel_data.description, "price": hotel_data.price}
    hotels.append(hotel)
    return hotel


@router.put("/{hotel_id}")
def update_hotel(hotel_id: int, hotel_data: Hotel):
    for hotel in hotels:
        if hotel_id == hotel["id"]:
            hotel["name"] = hotel_data.name
            hotel["description"] = hotel_data.description
            hotel["price"] = hotel_data.price
            return hotel
    return {"message": "Hotel not found"}


@router.patch(
    "/{hotel_id}",
    summary="Update hotel partially", 
    description="Update any fields that are provided"
)
def update_hotel_partially(hotel_id: int, hotel_data: HotelPatch):
    for hotel in hotels:
        if hotel_id == hotel["id"]:
            if hotel_data.name:
                hotel["name"] = hotel_data.name
            if hotel_data.description:
                hotel["description"] = hotel_data.description
            if hotel_data.price:
                hotel["price"] = hotel_data.price
            return hotel
    return {"message": "Hotel not found"}


@router.delete("/{hotel_id}")
def delete_hotel(hotel_id: int):
    for hotel in hotels:
        if hotel_id == hotel["id"]:
            hotels.remove(hotel)
            return {"message": "Hotel deleted successfully"}
    return {"message": "Hotel not found"}
