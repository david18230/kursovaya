from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_pagination, get_room_or_404, get_current_user
from app.core.redis import increment
from app.models.models import Room
from app.services.favourite_service import FavouriteService
from database import get_db
from app.schemas.room import RoomCreate, RoomResponse
from app.services.room_services import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])
@router.get("/", summary = "Получить информацию о номерах", operation_id = "list_rooms")
async def get_rooms(
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    room_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    capacity: int | None = None,
    date_in: date | None = None,
    date_out: date| None = None
):
    return await RoomService.get_filtered_rooms(db,
                                            room_type = room_type, min_price = min_price,
                                            max_price = max_price, capacity = capacity,
                                            date_in = date_in, date_out = date_out,
                                                offset = pagination["offset"],
                                                limit = pagination["limit"])

@router.get("/favourite", response_model=list[RoomResponse])
async def get_favorite_rooms(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    favourite_rooms = await FavouriteService.get_all(db, current_user.id)
    return favourite_rooms

@router.get("/{room_id}", summary = "Получить информацию о номере", operation_id = "get_room")
async def get_room_by_id(room_id: int, db: AsyncSession = Depends(get_db)):
    room = await get_room_or_404(room_id, db)
    await increment(f"rooms:views:{room_id}")
    return RoomResponse.model_validate(room)
@router.post("/{room_id}/favourite")
async def favourite_room(room_id: int, current_user = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    favourite_room = await FavouriteService.add_favourite(db, current_user.id, room_id)
    if favourite_room:
        return {"message": "Уже в избранном"}
    return {"message": "Добавлено в избранное"}

@router.delete("/{room_id}/favourite")
async def remove_favourite_room(room_id: int, current_user = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    favourite_room = await FavouriteService.remove_favourite(db, current_user.id, room_id)
    return favourite_room
