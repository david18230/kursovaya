from datetime import date, datetime
from sqlalchemy import String, Numeric, ForeignKey, Date, Integer, func, TIMESTAMP, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.models.enums import UserRole, BookingStatus, RoomType

class Base(DeclarativeBase): pass

class Room(Base):
    __tablename__ = "rooms"
    id:Mapped[int] = mapped_column(primary_key = True)
    room_number:Mapped[str] = mapped_column(String, unique = True, nullable = False)
    price_per_night:Mapped[float] = mapped_column(Numeric(10, 2), nullable = False)
    type:Mapped[RoomType] = mapped_column(String)
    capacity:Mapped[int] = mapped_column(Integer)
    created_at:Mapped[datetime] =mapped_column(TIMESTAMP(timezone = True), server_default = func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone = True), server_default = func.now(),
                                                 onupdate = func.now())
class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key = True)
    full_name:Mapped[str] = mapped_column(String, nullable = False)
    phone:Mapped[str] = mapped_column(String)
    email:Mapped[str] = mapped_column(String, index = True)
    role:Mapped[UserRole] = mapped_column(String, server_default = "user")
    hashed_password:Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone = True), server_default = func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone = True), server_default = func.now(),
                                                 onupdate = func.now())

class Booking(Base):
    __tablename__ = "bookings"
    id:Mapped[int] = mapped_column(primary_key = True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), index = True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index = True)
    date_in: Mapped[date] = mapped_column(Date, nullable = False, index = True)
    date_out: Mapped[date] = mapped_column(Date, nullable = False, index = True)
    status: Mapped[BookingStatus] = mapped_column(String, server_default = "pending",
                                                  nullable = False)
    guest_count: Mapped[int] = mapped_column(Integer, nullable = False)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable = False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone = True),
                                                 server_default = func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone = True),
                            server_default = func.now(), onupdate = func.now())

class Favourite(Base):
    __tablename__ = "favourites"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),
                                                 server_default=func.now())

class PromoCode(Base):
    __tablename__ = "promocode"
    id: Mapped[int] = mapped_column(primary_key = True)
    code: Mapped[str] = mapped_column(String, unique = True)
    discount_percent: Mapped[int] = mapped_column(Integer)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_until: Mapped[date] = mapped_column(Date)
    max_uses: Mapped[int] = mapped_column(Integer)
    used_count: Mapped[int] = mapped_column(Integer, server_default = "0")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default = "true")