from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User


class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, data):
        user = User(**data.model_dump())
        db.add(user)
        await db.commit()
        return user
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    @staticmethod
    async def login(db: AsyncSession, email: str, password: str):
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or user.password != password:
            return None
        return user
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        await db.delete(user)
        await db.commit()
        return user
    # @staticmethod
    # async def check_admin(db: AsyncSession, user_id: int):
    #     admin = await UserService.get_user_by_id(db, user_id)
    #     if not admin or admin.role != "admin":
    #         return None
    #     return admin
    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(User))
        return result.scalars().all()
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, data):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if data.full_name != None:
            user.full_name = data.full_name
        if data.phone != None:
            user.phone = data.phone
        if data.email != None:
            user.email = data.email
        if data.role != None:
            user.role = data.role
        if data.password != None:
            user.password = data.password
        await db.commit()
        await db.refresh(user)
        return user

