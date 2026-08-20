import re
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import UserRole

class UserCreate(BaseModel):
    full_name: str = Field(min_length = 2, pattern = r"^[а-яА-ЯёЁa-zA-Z\s-]+$",
                           json_schema_extra = {"example": "Иван Иванов"}, description = "Полное имя")
    phone: str = Field(json_schema_extra = {"example": "+79991234567"}, description = "Номер телефона")
    email: str = Field(json_schema_extra = {"example": "ivan@gmail.com"}, description = "Электронная почта")
    password: str = Field(min_length = 6, description = "Пароль минимум 6 символов")

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    full_name: str | None = Field(json_schema_extra = {"example": "Иван Иванов"},
                                  description = "Полное имя")
    phone: str | None = Field(json_schema_extra = {"example": "+79991234567"},
                              description = "Номер телефона")
    email: str | None = Field(json_schema_extra = {"example": "ivan@gmail.com"},
                              description = "Электронная почта")
    password: str | None = Field(None, min_length = 6, description = "Пароль минимум 6 символов",
                                 json_schema_extra = {"example": "••••••••"})
    role: UserRole | None = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: str
    role: UserRole | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes = True)