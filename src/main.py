from fastapi import FastAPI, Body, Query
import uvicorn
from src.api.hotels import router as router_hotels
from src.config import settings


print(settings.DB_NAME)

app = FastAPI()

app.include_router(router_hotels)



if __name__ == "__main__":
    uvicorn.run(app="src.main:app", reload=True) 


