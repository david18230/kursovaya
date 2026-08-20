from fastapi import HTTPException, Query
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.services.room_services import RoomService
from app.services.user_services import UserService
from database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_db)):

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Неверный токен")

    user = await UserService.get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user
async  def get_current_admin(token: str = Depends(oauth2_scheme), db:AsyncSession = Depends(get_db)):
    admin = await get_current_user(token, db)
    if admin.role != "admin":
        raise HTTPException(403, "Доступ только для админов")
    return admin

async def get_pagination(page: int =Query(1, ge = 1),
                         limit: int = Query(20, le = 100)):
    offset = (page - 1) * limit
    return {
        "offset": offset,
        "limit": limit
    }

async def get_room_or_404(room_id, db: AsyncSession = Depends(get_db)):
    room = await RoomService.get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(404, "Номер не найден")
    return room
