from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import json
from app.core.redis import get_cache, set_cache, redis_client, delete_pattern, exists_key
from app.models.models import Room, Booking
from app.schemas.room import RoomResponse
class RoomService:
    @staticmethod
    async def create_room(db: AsyncSession, data):
        room = Room(**data.dict())
        db.add(room)
        await db.commit()
        await redis_client.delete("rooms:all")
        await delete_pattern("rooms:filter*")
        return room
    @staticmethod
    async def get_all_rooms(db: AsyncSession):
        if await exists_key("rooms:all"):
            cached = await get_cache("rooms:all")
            return json.loads(cached)
        result = await db.execute(select(Room))
        rooms = result.scalars().all()
        rooms_data = [RoomResponse.model_validate(r).model_dump(mode='json') for r in rooms]
        await set_cache("rooms:all", json.dumps(rooms_data))
        return rooms_data

    @staticmethod
    async def get_room_by_id(db: AsyncSession, room_id: int):
        result = await db.execute(select(Room).where(Room.id == room_id))
        room = result.scalar_one_or_none()
        if not room:
            return None
        return room
    @staticmethod
    async def update_room(db: AsyncSession, room_id: int, data):
        result = await db.execute(select(Room).where(Room.id == room_id))
        room = result.scalar_one_or_none()
        if not room:
            return None
        if data.room_number != None:
            room.room_number = data.room_number
        if data.price_per_night != None:
            room.price_per_night = data.price_per_night
        if data.type != None:
            room.type = data.type
        if data.capacity != None:
            room.capacity = data.capacity
        await db.commit()
        await redis_client.delete("rooms:all")
        await delete_pattern("rooms:filter*")
        await db.refresh(room)
        return room
    @staticmethod
    async def delete_room(db: AsyncSession, room_id):
        result = await db.execute(select(Room).where(Room.id == room_id))
        room = result.scalar_one_or_none()
        if not room:
            return None
        await db.delete(room)
        await db.commit()
        await redis_client.delete("rooms:all")
        await delete_pattern("rooms:filter*")
        return room
    @staticmethod
    async def get_filtered_rooms(db: AsyncSession,
            offset: int, limit: int,
            room_type: str | None = None,
            min_price: float | None = None,
            max_price: float | None = None,
            capacity: int | None = None,
            date_in: date | None = None,
            date_out: date| None = None):
            cached = await get_cache("rooms:filter")
            if cached is not None:
                return json.loads(cached)
            filtered_room = select(Room).offset(offset).limit(limit)
            if room_type is not None:
                filtered_room = filtered_room.where(Room.type == room_type)
            if min_price is not None:
                filtered_room = filtered_room.where(Room.price_per_night >= min_price)
            if max_price is not None:
                filtered_room = filtered_room.where(Room.price_per_night <= max_price)
            if capacity is not None:
                filtered_room = filtered_room.where(Room.capacity >= capacity)
            if date_in is not None and date_out is not None:
                busy_rooms = select(Booking.room_id).where(Booking.date_in < date_out,
                    Booking.date_out > date_in, Booking.status != "cancelled")
                filtered_room = filtered_room.where(Room.id.not_in(busy_rooms))
            total = filtered_room.with_only_columns(func.count(Room.id)).order_by(None)
            page = offset // limit + 1
            total_rooms = (await db.execute(total)).scalar()
            pages = (total_rooms + limit - 1) // limit
            result = await db.execute(filtered_room)
            rooms = result.scalars().all()
            rooms_data = [RoomResponse.model_validate(r).model_dump(mode = "json") for r in rooms]
            await set_cache("rooms:filter*", json.dumps(rooms_data))
            return { "data": rooms_data,
                     "total": total_rooms,
                     "page": page,
                     "limit": limit,
                     "pages": pages}

    @staticmethod
    async def search_rooms(db: AsyncSession, q):
        search_room = await db.execute(select(Room).where(Room.room_number.ilike(f"%{q}%")
                                                          | Room.type.ilike(f"%{q}%")))
        return search_room.scalars().all()