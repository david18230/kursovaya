from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_services import UserService
from database import get_db


router = APIRouter(prefix = "/users", tags = ["Users"])
@router.get("/me")
async def get_me(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    return user
@router.put("/update/me")
async def update_me(user_id: int,  data: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await UserService.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    return {
        "message" : "Profile updated",
        "user" : user
    }
@router.delete("/delete/me")
async def delete_me(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService.delete_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return {
        "message": "Profile deleted"
    }