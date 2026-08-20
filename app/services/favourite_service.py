from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Favourite, Room

class FavouriteService:
    @staticmethod
    async def add_favourite(db: AsyncSession, user_id: int, room_id: int):
        result = await db.execute(select(Favourite).where(Favourite.user_id == user_id,
                                                          Favourite.room_id == room_id))
        existing = result.scalar_one_or_none()
        if existing:
            return False
        favourite = Favourite(user_id=user_id, room_id=room_id)
        db.add(favourite)
        await db.commit()
        return True

    @staticmethod
    async def remove_favourite(db: AsyncSession, user_id: int, room_id: int):
        result = await db.execute(select(Favourite).where(Favourite.user_id == user_id,
                                                          Favourite.room_id == room_id))
        existing = result.scalar_one_or_none()
        if existing:
            await db.delete(existing)
        await db.commit()
        return existing

    @staticmethod
    async def get_all(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(Room).join(Favourite, Favourite.room_id == Room.id)
            .where(Favourite.user_id == user_id)
        )
        return result.scalars().all()