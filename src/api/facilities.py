from fastapi import APIRouter, Body
from src.schemas.facilities import FacilityAdd
from src.api.dependencies import DBDep
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.get("")
@cache(expire=10)
async def get_all_facilities(db: DBDep):
    print("FROM DB")
    facilities = await db.facilities.get_all()
    return facilities


@router.post("")
async def create_facility(
    db: DBDep,
    facility_data: FacilityAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Wi-Fi",
                "value": {
                    "title": "Wi-Fi",
                },
            },
            "2": {
                "summary": "TV",
                "value": {
                    "title": "TV",
                },
            },
        }
    ),
):
    facility = await db.facilities.add(facility_data)
    await db.commit()
    return {"status": "OK", "data": facility}
