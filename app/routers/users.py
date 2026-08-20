from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_services import UserService
from database import get_db

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

router = APIRouter(prefix = "/users", tags = ["Users"])
@router.get("/me", operation_id = "get_me", summary = "Получить себя")
async def get_me(current_user: AsyncSession = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.put("/update/me", operation_id = "update_me", summary = "Обновить себя")
async def update_me(data: UserUpdate, db: AsyncSession = Depends(get_db),
                    current_user = Depends(get_current_user)):
    new_current_user = await UserService.update_user(db, current_user.id, data)
    if not new_current_user:
        raise HTTPException(404, "User not found")
    return {
        "message" : "Profile updated",
        "user": UserResponse.model_validate(new_current_user)
    }

@router.delete("/delete/me", operation_id = "delete_me", summary = "Удалить себя")
async def delete_me(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    deleted_user = await UserService.delete_user(db, current_user.id)
    if not deleted_user:
        raise HTTPException(404, "User not found")
    return {
        "message": "Profile deleted"
    }





@router.patch("/change-password", operation_id="change_password", summary="Смена пароля")
async def change_password(data: ChangePassword,
                current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    changed_password = await UserService.change_password(db, current_user.id, data.old_password, data.new_password)
    if changed_password is False:
        raise HTTPException(400, "Неверный старый пароль")
    return {"message": "Пароль изменен"}