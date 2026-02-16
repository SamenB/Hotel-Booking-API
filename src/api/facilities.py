from fastapi import APIRouter, Body
from fastapi.exceptions import HTTPException
from src.schemas.facilities import FacilityAdd
from src.api.dependencies import DBDep
from src.exeptions import ObjectAlreadyExistsException, DatabaseException
from src.services.facilities import FacilityService
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.get("")
@cache(expire=10)
async def get_all_facilities(db: DBDep):
    try:
        return await FacilityService(db).get_all_facilities()
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


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
    try:
        facility = await FacilityService(db).create_facility(facility_data)
    except ObjectAlreadyExistsException:
        raise HTTPException(status_code=409, detail="Facility already exists")
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK", "data": facility}
