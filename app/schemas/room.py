from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import RoomType

class RoomCreate(BaseModel):
    room_number: str
    price_per_night: float = Field(gt = 0)
    type: RoomType
    capacity: int = Field(gt = 0)

class RoomUpdate(BaseModel):
    room_number: str | None = None
    price_per_night: float | None = Field(gt = 0, json_schema_extra = {"example": 5000})
    type: str | None = Field(json_schema_extra = {"example": "люкс"})
    capacity: int | None = Field(json_schema_extra = {"example": 2})

class RoomResponse(BaseModel):
    id: int
    room_number: str
    price_per_night: float
    type: RoomType
    capacity: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes = True)