from dotenv import load_dotenv

from app.core.redis import reset_online

load_dotenv()
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from app.middleware import LoggingMiddleware
from app.models.models import Base
from database import engine
from app.routers.rooms import router as rooms_router
from app.routers.bookings import router as bookings_router
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.health import router as health_router

logger.add("logs/app.log", rotation = "10 MB", retention = "7 days", level = "INFO")
logger.add("logs/app.json", rotation = "10 MB", retention = "7 days", serialize = True)
logger.add("logs/errors.log", level="ERROR")
logger.add("logs/sql.log", filter="sqlalchemy", rotation="10 MB", retention="7 days")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        await reset_online()
        await engine.dispose()

app = FastAPI(lifespan = lifespan)

@app.exception_handler(404)
async def error_404(request, exc):
    request_id = request.headers.get("X-Request-ID")
    return JSONResponse(status_code = 404, content = {
        "status": "error",
        "code": 404,
        "message": "Ресурс не найден",
        "request_id": request_id,
        "path": request.url.path,
        "timestamp": datetime.now().isoformat()
    } )

@app.exception_handler(500)
async def error_500(request, exc):
    request_id = request.headers.get("X-Request-ID")
    return JSONResponse(status_code = 500, content = {
        "status": "error",
        "code": 500,
        "message": "Внутренняя ошибка сервера",
        "request_id": request_id,
        "path": request.url.path,
        "timestamp": datetime.now().isoformat()
    } )

@app.get("/")
async def root():
    return {
        "name": "HotelAPI",
        "version": "1.0.0",
        "docs": "/docs"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(GZipMiddleware)
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(health_router)
