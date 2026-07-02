from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.schemas.room import RoomCreate
from app.services.room_services import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])
@router.get("/rooms")
async def get_rooms(db: AsyncSession = Depends(get_db)):
    return await RoomService.get_all_rooms(db)
# @router.get("/")
# async def get_rooms(
#         min_price:float = None,
#         max_price:float = None,
#         capacity:int = None,
#         db: AsyncSession = Depends(get_db)
# ):
