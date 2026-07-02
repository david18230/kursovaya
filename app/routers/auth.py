from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserLogin
from app.services.user_services import UserService
from database import get_db
import re
router = APIRouter(prefix = "/auth", tags = ["Auth"])
@router.post("/register")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    if  not re.match(r"^8[+7]\d{10}$", data.phone):
        raise HTTPException(
        status_code = 400,
        detail = "Номер телефона должен содержать 10-11 цифр и может начинаться с +7 или 8")
    return await UserService.create_user(db, data)
@router.post("/login")
async def login(data: UserLogin, db:AsyncSession = Depends(get_db)):
    user = await UserService.login(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code = 401, detail = "User not found")
    return {"message": "login success", "user_id": user.id}
