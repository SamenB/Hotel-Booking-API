from fastapi import FastAPI, Body, Query
import uvicorn


app = FastAPI()


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

@app.get("/hotels")
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


@app.post("/hotels")
def create_hotel(
    hotel_name: str = Body(..., embed=True, description="Hotel name")
    ):
    hotel_id = len(hotels) + 1
    hotel = {"id": hotel_id, "name": hotel_name}
    hotels.append(hotel)
    return hotel

@app.put("/hotels/{hotel_id}")
def update_hotel(
    hotel_id: int,
    hotel_name: str = Body(..., embed=True, description="Hotel name"),
    hotel_description: str = Body(..., embed=True, description="Hotel description"),
    hotel_price: int = Body(..., embed=True, description="Hotel price")
):
    for hotel in hotels:
        if hotel_id == hotel["id"]:
            hotel["name"] = hotel_name
            hotel["description"] = hotel_description
            hotel["price"] = hotel_price
            return hotel
    return {"message": "Hotel not found"}


@app.patch(
    "/hotels/{hotel_id}",
    summary="Update hotel partially", 
    description="Update any fields that are provided"
)
def update_hotel_partially(
    hotel_id: int,
    hotel_name: str | None = Body(None, embed=True, description="Hotel name"),
    hotel_description: str | None = Body(None, embed=True, description="Hotel description"),
    hotel_price: int | None = Body(None, embed=True, description="Hotel price")
):
    for hotel in hotels:
        if hotel_id == hotel["id"]:
            if hotel_name:
                hotel["name"] = hotel_name
            if hotel_description:
                hotel["description"] = hotel_description
            if hotel_price:
                hotel["price"] = hotel_price
            return hotel
    return {"message": "Hotel not found"}


@app.delete("/hotels/{hotel_id}")
def delete_hotel(hotel_id: int):
    for hotel in hotels:
        if hotel_id == hotel["id"]:
            hotels.remove(hotel)
            return {"message": "Hotel deleted successfully"}
    return {"message": "Hotel not found"}

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True) 


