from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Booking
from app.services.room_services import RoomService


class BookingService:
    @staticmethod
    async def create_booking(db: AsyncSession, data):
        booking = Booking(**data.dict())
        room = await RoomService.get_room_by_id(db, data.room_id)
        if room is None:
            return None
        nights = (data.date_out - data.date_in).days
        total_price = nights * room.price_per_night
        booking = Booking(
            user_id=data.user_id,
            room_id=data.room_id,
            date_in=data.date_in,
            date_out=data.date_out,
            guest_count=data.guest_count,
            total_price=total_price
        )
        db.add(booking)
        await db.commit()
        return booking
    @staticmethod
    async def delete_booking(db: AsyncSession, booking_id: int):
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalar_one_or_none()
        if not booking:
            return None
        await db.delete(booking)
        await db.commit()
        return booking
    @staticmethod
    async def get_by_id(db: AsyncSession, booking_id: int):
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(Booking))
        return result.scalars().all()
    @staticmethod
    async def update_booking(db: AsyncSession, booking_id: int, data):
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalar_one_or_none()
        if not booking:
            return None
        if data.date_in != None:
            booking.date_in = data.date_in
        if data.date_out != None:
            booking.date_out = data.date_out
        await db.commit()
        await db.refresh(booking)
        return booking
