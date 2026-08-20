import json
from http.client import HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, verify_password, validate_password_strength
from app.models.enums import UserRole
from app.models.models import User
from app.schemas.user import UserResponse

class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, data):
        user = User(full_name = data.full_name,
                    phone = data.phone,
                    email = data.email,
                    role = UserRole.USER,
                    hashed_password = hash_password(data.password)
                    )
        existed_email = await db.execute(select(User).where(User.email == data.email))
        if existed_email.scalar_one_or_none():
            return "email_exists"
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
        if not user:
            return None
        elif verify_password(password, user.hashed_password):
            return user
        else:
            return None

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        await db.delete(user)
        await db.commit()
        return user
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
            user.hashed_password = hash_password(data.password)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def change_password(db: AsyncSession, user_id, old_password, new_password):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not verify_password(old_password, user.hashed_password):
            return False
        new_hashed_password = hash_password(new_password)
        user.hashed_password = new_hashed_password
        await db.commit()

    @staticmethod
    async def search_users(db: AsyncSession, q):
        search_user = await db.execute(select(User).where(User.full_name.ilike(f"%{q}%")
                                                          | User.email.ilike(f"%{q}")))
        return search_user.scalars().all()