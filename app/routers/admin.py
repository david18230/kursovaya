from fastapi import HTTPException

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.room import RoomCreate
from app.services.booking_services import BookingService
from app.services.room_services import RoomService
from app.services.user_services import UserService
from database import get_db

router = APIRouter(prefix = "/admin", tags = ["Admin"])

async def check_admin(db: AsyncSession, admin_id: int):
    admin = await UserService.get_user_by_id(db, admin_id)
    if not admin or admin.role != "admin":
        return None
    return admin
@router.get("/users")
async def get_users(admin_id: int, db: AsyncSession = Depends(get_db)):
    admin = await check_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code = 404, detail = "Admin not found")
    return await UserService.get_all(db)
@router.delete("/user/{user_id}")
async def delete_user(user_id: int, admin_id: int, db: AsyncSession = Depends(get_db)):
    admin = await check_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    if user_id == admin_id:
        raise HTTPException(status_code = 403, detail = "Админ не может удалить себя")
    user = await UserService.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    return {
        "message" : "User deleted"
    }

@router.get("/users/{user_id}")
async def get_user(user_id: int, admin_id: int, db: AsyncSession = Depends(get_db)):
    admin = await check_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
@router.get("/bookings")
async def get_bookings(admin_id: int, db: AsyncSession = Depends(get_db)):
    admin = await check_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return await BookingService.get_all(db)
@router.get("/bookings/{booking_id}")
async def get_booking(booking_id: int, admin_id: int, db: AsyncSession = Depends(get_db)):
    admin = await check_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    booking = await BookingService.get_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="User not found")
    return booking
@router.get("/rooms")
async def get_rooms(admin_id: int, db: AsyncSession = Depends(get_db)):
    admin = await check_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return await RoomService.get_all_rooms(db)
@router.get("/rooms/{room_id}")
async def get_room_by_id(room_id: int, admin_id: int, db: AsyncSession = Depends(get_db)):
    admin = await check_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    room = await RoomService.get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room
@router.post("/")
async def create_room(data:RoomCreate,db:AsyncSession=Depends(get_db)):
    if data.price < 0:
        raise HTTPException(status_code=400, detail="Некорректная цена")
    return await RoomService.create_room(db, data)