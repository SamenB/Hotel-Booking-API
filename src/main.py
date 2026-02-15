from fastapi import FastAPI
import uvicorn
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from src.api.hotels import router as router_hotels
from src.api.auth import router as router_auth
from src.api.rooms import router as router_rooms, bulk_router as rooms_bulk_router
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities
from src.init import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()  # when app starts
    assert redis_manager.redis is not None
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    yield
    await redis_manager.close()  # when app stops/restarts


app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(rooms_bulk_router)
app.include_router(router_bookings)
app.include_router(router_facilities)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app="src.main:app", reload=True)
