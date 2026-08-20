from fastapi import HTTPException, BackgroundTasks
from fastapi import APIRouter
from fastapi.params import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_admin
from app.core.redis import redis_client
from app.schemas.booking import BookingResponse
from app.schemas.promocodes import PromocodeCreate
from app.schemas.room import RoomCreate, RoomUpdate
from app.services.booking_services import BookingService
from app.services.notifications import send_payment_congirmation
from app.services.promocode_service import PromoCodeService
from app.services.room_services import RoomService
from app.services.user_services import UserService
from database import get_db
router = APIRouter(prefix = "/admin", tags = ["Admin"])
@router.get("/users", operation_id = "admin_list_users")
async def get_users(admin = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await UserService.get_all(db)
@router.delete("/user/{user_id}")
async def delete_user(user_id: int, admin_id = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    user = await UserService.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    logger.info(f"Админ удалил пользователя с id = {user_id}")
    return { "message" : "User deleted" }
@router.get("/users/{user_id}", operation_id = "admin_get_user")
async def get_user(user_id: int, admin_id = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    user = await UserService.get_user_by_id(db, user_id)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/bookings", operation_id = "admin_list_bookings")
async def get_bookings(admin_id: int = Depends(get_current_admin),
                       db: AsyncSession = Depends(get_db)):
    return await BookingService.get_all(db)

@router.get("/bookings/{booking_id}", operation_id = "admin_get_booking")
async def get_booking(booking_id: int, admin_id= Depends(get_current_admin),
                      db: AsyncSession = Depends(get_db)):

    booking = await BookingService.get_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="User not found")
    return booking

@router.get("/rooms", operation_id = "admin_list_rooms")
async def get_rooms(admin_id=Depends(get_current_admin), db: AsyncSession=Depends(get_db)):
    return await RoomService.get_all_rooms(db)

@router.get("/rooms/{room_id}", operation_id = "admin_get_room")
async def get_room_by_id(room_id: int, admin_id = Depends(get_current_admin),
                         db: AsyncSession = Depends(get_db)):
    room = await RoomService.get_room_by_id(db, room_id)
    if not room: raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.post("/", operation_id = "admin_create_room")
async def create_room(data:RoomCreate,db:AsyncSession=Depends(get_db),admin_id=Depends(get_current_admin)):
    if data.price_per_night < 0: raise HTTPException(status_code=400, detail="Некорректная цена")
    return await RoomService.create_room(db, data)

@router.put("/rooms/{room_id}", operation_id = "admin_update_room")
async def update_room(room_id: int, data: RoomUpdate, db: AsyncSession = Depends(get_db),
                      admin_id = Depends(get_current_admin)):
    room = await RoomService.update_room(db, room_id, data)
    if not room: raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.delete("/rooms/{room_id}", operation_id = "admin_delete_room")
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db), admin_id = Depends(get_current_admin)):
    room = await RoomService.delete_room(db, room_id)
    if not room:  raise HTTPException(404, "Room not found")
    return {"message": "Room deleted"}
@router.get("/stats/online")
async def online_users():
    count = await redis_client.get("online_users")
    return {"online": int(count) or 0}

@router.get("/search")
async def get_search(q: str, db: AsyncSession = Depends(get_db),
                     current_user = Depends(get_current_admin)):
    rooms = await RoomService.search_rooms(db, q)
    users = await UserService.search_users(db, q)
    bookings = await BookingService.search_bookings(db, q)
    return {
        "rooms": rooms,
        "users": users,
        "bookings": bookings
    }
@router.patch("/pay/{booking_id}")
async def pay_booking(background_tasks: BackgroundTasks, booking_id: int,
                    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_admin)):
    booking = await BookingService.pay_booking(db, booking_id)
    if booking is None: raise HTTPException(404, "Бронь не найдена")
    if booking is False:
        raise HTTPException(400, "Нельзя оплатить эту бронь")
    background_tasks.add_task(send_payment_congirmation, booking.id, booking.user_id)
    return BookingResponse.model_validate(booking)
@router.post("/promocode")
async def create_promocode(data: PromocodeCreate,
                           db: AsyncSession = Depends(get_db),
                           admin_id = Depends(get_current_admin)):
    return await PromoCodeService.create_promocode(db, data)
@router.get("/promocodes")
async def get_promocodes(db: AsyncSession = Depends(get_db),
                           admin_id = Depends(get_current_admin)):
    return await PromoCodeService.get_all(db)
