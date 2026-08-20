from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import BookingStatus

class BookingCreate(BaseModel):
    room_id: int = Field(description = "ID номера")
    user_id: int | None = Field(None, description="ID пользователя")
    date_in: date = Field(json_schema_extra = {"example" : "2026-08-04"}, description = "Дата заезда")
    date_out: date = Field(json_schema_extra = {"example" : "2026-08-04"}, description = "Дата выезда")
    guest_count: int = Field(json_schema_extra = {"example": 2}, description = "Количество гостей")
    promo_code: str | None = None

class BookingUpdate(BaseModel):
    room_id: int| None =Field(None, description = "ID номера")
    user_id: int | None = Field(None, description = "ID пользователя")
    date_in: date | None = Field(None, json_schema_extra = {"example" : "2026-08-01"}, description = "Дата заезда")
    date_out: date | None = Field(None, json_schema_extra = {"example" : "2026-08-04"}, description = "Дата выезда")
    guest_count: int | None = Field(None, json_schema_extra = {"example": 2},  description = "Количество гостей")
    status: BookingStatus | None = Field(None, description = "Статус брони")

class BookingResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    date_in: date
    date_out: date
    guest_count: int
    total_price: float
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes = True)


