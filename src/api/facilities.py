from fastapi import APIRouter, Body, Query
from src.schemas.facilities import FacilityAdd
from src.api.dependencies import DBDep

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.get("")
async def get_all_facilities(db: DBDep):
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
