from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.core import redis
from app.core.redis import is_rate_limited, incr_online, decr_online
from app.core.security import create_access_token, validate_password_strength, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.notifications import send_welcome_notification
from app.services.user_services import UserService
from database import get_db
import re

router = APIRouter(prefix = "/auth", tags = ["Auth"])
@router.post("/register", operation_id = "register")
async def register(background_tasks: BackgroundTasks, data: UserCreate,  db: AsyncSession = Depends(get_db)):
    result = await UserService.create_user(db, data)
    if result == "email_exists":
        raise HTTPException(409, "Email уже зарегистрирован")
    if result is None:
        raise HTTPException(400, "Пароль слишком слабый")
    token = create_access_token({
        "sub": str(result.id),
        "role": result.role
    })
    background_tasks.add_task(send_welcome_notification,result.id, result.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": result
    }

@router.post("/login", operation_id = "login", summary = "Войти")
async def login(data: UserLogin, db:AsyncSession = Depends(get_db)):
    key = f"login_attempt: {data.username}"
    if await is_rate_limited(key, 5, 600):
        raise HTTPException(429, "Слишком много попыток входа. Попробуйте через 10 минут")
    user = await UserService.login(db, data.username, data.password)
    if not user:
        logger.warning(f"Неудачная попытка входа: {data.username}")
        raise HTTPException(status_code = 401, detail = "User not found")
    await incr_online()

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/logout")
async def logout():
    await decr_online()
    return {
        "message": "Вы вышли"
    }