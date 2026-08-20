from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user
from app.core.redis import add_booking_to_rating, is_rate_limited
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.services.booking_services import BookingService
from app.services.notifications import send_booking_notification
from app.services.room_services import RoomService
from database import get_db
router = APIRouter(prefix="/bookings", tags=["Bookings"])
@router.post("/", operation_id = "create_booking", summary = "Создать бронь")
async def create_booking(background_tasks: BackgroundTasks, data:BookingCreate,
                    db:AsyncSession=Depends(get_db), current_user = Depends(get_current_user)):
    key = f"booking_attempt: {current_user.id}"
    if await is_rate_limited(key, 3, 60): raise HTTPException(429, "Слишком много попыток создания брони")
    room = await RoomService.get_room_by_id(db, data.room_id)
    if room is None: raise HTTPException(status_code=404, detail="Такого номера нет")
    if data.date_out < data.date_in:
        raise HTTPException(status_code = 400, detail = "Дата выезда раньше даты заезда")
    if data.date_out == data.date_in:
        raise HTTPException(status_code = 400, detail = "Дата выезда не может совпадать с датой заезда")
    if data.date_out < date.today():
        raise HTTPException(status_code = 400, detail = "Дата заезда не может быть в прошлом")
    if data.guest_count > room.capacity:
        raise HTTPException(status_code = 400, detail = "Количество гостей больше вместимости номера")
    data.user_id = current_user.id
    booking = await BookingService.create_booking(db, data)
    if booking is False: raise HTTPException(409, "Номер занят на эти даты")
    if booking is None: raise HTTPException(404, "Не удалось создать бронь")
    background_tasks.add_task(send_booking_notification, booking.id, booking.user_id)
    return BookingResponse.model_validate(booking)

@router.delete("/delete/{booking_id}", operation_id = "delete_booking", summary = "Удалить бронь")
async def delete_booking(booking_id: int, db: AsyncSession = Depends(get_db),
                         current_user = Depends(get_current_user)):
    booking = await BookingService.delete_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code = 404, detail = "Booking not found")
    days_until = (booking.date_in - date.today()).days
    if days_until < 2:
        raise HTTPException(403, "Бронь нельзя удалить за 2 до дня до даты заезда")
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Это не ваша бронь")
    return {"message": "Booking deleted"}

@router.get("/get/{booking_id}", operation_id = "get_booking", summary = "Получить бронирование")
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_db),
                      current_user = Depends(get_current_user)):
    booking = await BookingService.get_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code = 404, detail = "Booking not found")
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Это не ваша бронь")
    days_left = (booking.date_in - datetime.now().date()).days
    return {"booking": BookingResponse.model_validate(booking), "days_left": days_left}

@router.put("/update/{booking_id}", operation_id = "update_booking", summary = "Обновить бронирование")
async def update_booking(booking_id: int, data: BookingUpdate, db: AsyncSession = Depends(get_db),
                         current_user = Depends(get_current_user)):
    booking = await BookingService.update_booking(db, booking_id, data)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Это не ваша бронь")
    return {
        "message": "Booking updated",
        "booking": BookingResponse.model_validate(booking)
    }
@router.patch("/cancel/{booking_id}", operation_id="cancel_booking", summary = "Отменить бронирование")
async def cancel_booking(booking_id: int, current_user = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    booking = await BookingService.cancel_booking(db, booking_id, current_user.id)
    if booking is None:
        raise HTTPException(404, "Бронь не найдена")
    if booking is False:
        raise HTTPException(409, "Вы не можете отменить эту бронь")
    return BookingResponse.model_validate(booking)

@router.get("/my")
async def get_my_bookings(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    bookings = await BookingService.get_my_bookings(db, current_user.id)
    return [BookingResponse.model_validate(b) for b in bookings]