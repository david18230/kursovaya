from fastapi import FastAPI
from app.models.models import Base
from database import engine
from app.routers.rooms import router as rooms_router
from app.routers.bookings import router as bookings_router
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(users_router)