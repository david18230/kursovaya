import asyncio
import json
from datetime import date
from decimal import Decimal
from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.redis import add_booking_to_rating, exists_key, get_cache, set_cache, redis_client
from app.models.enums import BookingStatus
from app.models.models import Booking
from app.schemas.booking import BookingResponse
from app.services.promocode_service import PromoCodeService
from app.services.room_services import RoomService

class BookingService:
    @staticmethod
    async def is_room_available(db: AsyncSession, room_id: int, date_in: date, date_out: date) -> bool:
        selected_room = select(func.count(Booking.id)).where(
            Booking.room_id == room_id,
            Booking.date_in < date_out,
            Booking.date_out > date_in,
            Booking.status != "cancelled")
        result = await db.execute(selected_room)
        count = result.scalar()
        return count == 0

    @staticmethod
    async def create_booking(db: AsyncSession, data):
        room = await RoomService.get_room_by_id(db, data.room_id)
        if room is None:
            return None
        busy_room = await BookingService.is_room_available(db, data.room_id, data.date_in, data.date_out)
        if busy_room is False:
            logger.warning(f"Попытка забронировать занятый номер {data.room_id}"
                           f" на даты {data.date_in} - {data.date_out}")
            return None
        nights = (data.date_out - data.date_in).days
        total_price = nights * room.price_per_night
        if data.promo_code:
            promo = await PromoCodeService.validate_promo(db, data.promo_code)
            if promo:
                total_price = total_price * (1 - Decimal(promo.discount_percent / 100))
                promo.used_count += 1
        booking = Booking(user_id=data.user_id, room_id=data.room_id,
            date_in=data.date_in, date_out=data.date_out,
            guest_count=data.guest_count, total_price=total_price)
        db.add(booking)
        await db.commit()
        await add_booking_to_rating(data.room_id)
        await redis_client.delete(f"bookings:user:{data.user_id}")
        return booking
    @staticmethod
    async def delete_booking(db: AsyncSession, booking_id: int):
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalar_one_or_none()
        if not booking:
            return None
        await db.delete(booking)
        await db.commit()
        await redis_client.delete("bookings:all")
        await redis_client.delete(f"bookings:user:{booking.user_id}")
        return booking
    @staticmethod
    async def get_by_id(db: AsyncSession, booking_id: int):
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalar_one_or_none()
    @staticmethod
    async def get_all(db: AsyncSession):
        if await exists_key("bookings:all"):
            cached = await get_cache("bookings:all")
            return json.loads(cached)
        result = await db.execute(select(Booking))
        bookings = result.scalars().all()
        booking_data = [BookingResponse.model_validate(b).model_dump(mode="json") for b in bookings]
        await set_cache("bookings:all", json.dumps(booking_data), ttl=60)
        return booking_data
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
        if data.status != None:
            return None
        if data.guest_count != None:
            booking.guest_count = data.guest_count
        await db.commit()
        await redis_client.delete("bookings:all")
        await redis_client.delete(f"bookings:user:{data.user_id}")
        await db.refresh(booking)
        return booking



    @staticmethod
    async def search_bookings(db: AsyncSession, q):
        if q.isdigit():
            search_booking = await db.execute(select(Booking).where(Booking.id == int(q)))
            return search_booking.scalars().all()

    @staticmethod
    async def cancel_booking(db: AsyncSession, booking_id: int, user_id: int):
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalar_one_or_none()
        if booking.user_id != user_id: return None
        booking_status = BookingStatus(booking.status) if isinstance(booking.status, str) else booking.status
        if not booking_status.can_transition_to(BookingStatus.CANCELLED): return False
        booking.status = BookingStatus.CANCELLED
        await db.commit()
        await redis_client.delete("bookings:all")
        await redis_client.delete(f"bookings:user:{booking.user_id}")
        await db.refresh(booking)
        return booking
    @staticmethod
    async def pay_booking(db: AsyncSession, booking_id: int):
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalar_one_or_none()
        if not booking: return None
        if booking.status != BookingStatus.PENDING: return False
        booking.status = BookingStatus.CONFIRMED
        await db.commit()
        await db.refresh(booking)
        await redis_client.delete(f"bookings:user:{booking.user_id}")
        return booking
    @staticmethod
    async def get_my_bookings(db: AsyncSession, user_id: int):
        cache_key = f"bookings:user:{user_id}"
        if await exists_key(cache_key):
            cached = await get_cache(cache_key)
            return json.loads(cached)
        result = await db.execute(select(Booking).where(Booking.user_id == user_id))
        bookings = result.scalars().all()
        booking_data = [BookingResponse.model_validate(b).model_dump(mode="json") for b in bookings]
        await set_cache(cache_key, json.dumps(booking_data), ttl=60)
        return booking_data