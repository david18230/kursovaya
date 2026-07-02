from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    full_name: str
    phone: str
    email: str
    password: str = Field(min_length = 6, description = "Пароль минимум 6 символов")
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    password: str | None = None
    role: str | None = None