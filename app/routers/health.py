from fastapi import APIRouter, Depends
from sqlalchemy import text
from starlette.responses import JSONResponse

from app.core.redis import redis_client
from database import get_db

router = APIRouter(tags = ["Health"])
@router.get("/health")
async def health(db = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except:
        db_status = "disconnected"
    try:
        await redis_client.ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"
    if db_status == "connected" and redis_status == "connected":
        return {"status": "ok", "database": db_status, "redis": redis_status}
    else:
        return JSONResponse(status_code = 503, content = {"status": "error",
                                "database": db_status, "redis": redis_status})