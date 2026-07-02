from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.booking import BookingCreate, BookingUpdate
from app.services.booking_services import BookingService
from app.services.room_services import RoomService
from database import get_db

router = APIRouter(prefix="/bookings", tags=["Bookings"])
@router.post("/")
async def create_booking(data:BookingCreate,db:AsyncSession=Depends(get_db)):
    if data.date_out < data.date_in:
        raise HTTPException(status_code = 400, detail = "Дата выезда раньше даты заезда")
    if data.date_out == data.date_in:
        raise HTTPException(status_code = 400, detail = "Дата выезда не может"
                                                        " совпадать с датой заезда")
    if data.date_out < date.today():
        raise HTTPException(status_code = 400, detail = "Дата заезда не может быть в прошлом")
    room = await RoomService.get_room_by_id(db, data.room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Такого номера нет")
    if data.guest_count > room.capacity:
        raise HTTPException(status_code = 400, detail = "Количество гостей больше"
                                                        " вместимости номера")
    return await BookingService.create_booking(db, data)

@router.delete("/delete/{booking_id}")
async def delete_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    booking = await BookingService.delete_booking(db, booking_id)
    days_until = (booking.date_in - date.today()).days
    if days_until < 2:
        raise HTTPException(
            403,
            "Бронь нельзя удалить за 2 до дня до даты заезда")
    if not booking:
        raise HTTPException(status_code = 404, detail = "Booking not found")
    return {"message": "Booking deleted"}

@router.get("/get/{booking_id}")
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    booking = await BookingService.get_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code = 404, detail = "Booking not found")
    return booking
@router.put("/update/{booking_id}")
async def update_booking(booking_id: int, data: BookingUpdate, db: AsyncSession = Depends(get_db)):
    booking = await BookingService.update_booking(db, booking_id, data)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {
        "message": "Booking updated",
        "booking": booking
    }
