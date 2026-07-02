from datetime import date

from sqlalchemy import String, Numeric, ForeignKey, Date, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.testing.schema import mapped_column


class Base(DeclarativeBase): pass

class Room(Base):
    __tablename__ = "rooms"
    id:Mapped[int] = mapped_column(primary_key = True)
    room_number:Mapped[str] = mapped_column(String, unique = True,
                                            nullable = False)
    price_per_night:Mapped[float] = mapped_column(Numeric(10, 2),
                                                  nullable = False)
    type:Mapped[str] = mapped_column(String)
    capacity:Mapped[int] = mapped_column(Integer)
class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key = True)
    full_name:Mapped[str] = mapped_column(String, nullable = False)
    phone:Mapped[str] = mapped_column(String)
    email:Mapped[str] = mapped_column(String)
    role:Mapped[str] = mapped_column(String)
    password:Mapped[str] = mapped_column(String)
class Booking(Base):
    __tablename__ = "bookings"
    id:Mapped[int] = mapped_column(primary_key = True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    date_in: Mapped[date] = mapped_column(Date, nullable = False)
    date_out: Mapped[date] = mapped_column(Date, nullable=False)
    guest_count: Mapped[int] = mapped_column(Numeric, nullable = False)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)