from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Room

class RoomService:
    @staticmethod
    async def create_room(db: AsyncSession, data):
        room = Room(**data.dict())
        db.add(room)
        await db.commit()
        return room
    @staticmethod
    async def get_all_rooms(db: AsyncSession):
        result = await db.execute(select(Room))
        return result.scalars().all()

    @staticmethod
    async def get_room_by_id(db: AsyncSession, room_id: int):
        result = await db.execute(select(Room).where(Room.id == room_id))
        room = result.scalar_one_or_none()
        if not room:
            return None
        return room