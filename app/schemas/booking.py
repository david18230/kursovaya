from datetime import date

from pydantic import BaseModel


class BookingCreate(BaseModel):
    room_id: int
    user_id: int
    date_in: date
    date_out: date
    guest_count: int

class BookingUpdate(BaseModel):
    room_id: int
    user_id: int
    date_in: date | None = None
    date_out: date | None = None
    guest_count: int
