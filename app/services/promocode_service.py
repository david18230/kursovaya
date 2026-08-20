from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import PromoCode

class PromoCodeService:
    @staticmethod
    async def create_promocode(db: AsyncSession, data):
        promocode = PromoCode(**data.dict())
        db.add(promocode)
        await db.commit()
        return promocode
    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(PromoCode))
        promocodes = result.scalars().all()
        return promocodes
    @staticmethod
    async def validate_promo(db: AsyncSession, code: str):
        result = await db.execute(select(PromoCode).where(PromoCode.code == code))
        promo = result.scalar_one_or_none()
        if promo is None:
            return None
        elif promo.is_active == False:
            return False
        elif date.today() < promo.valid_from:
            return False
        elif date.today() > promo.valid_until:
            return False
        elif promo.used_count >= promo.max_uses:
            return False
        return promo
