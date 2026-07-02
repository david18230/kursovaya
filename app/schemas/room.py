from pydantic import BaseModel
class RoomCreate(BaseModel):
    room_number: str
    price_per_night: float
    type: str
    capacity: int