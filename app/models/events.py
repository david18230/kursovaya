
from datetime import date, datetime
import time
from loguru import logger
from sqlalchemy import event, select, func, Engine
from sqlalchemy.orm import Session
from app.models.models import User, Room, Booking

@event.listens_for(User, "before_insert")
def email_to_lower(mapper, connection, target):
    target.email = target.email.lower()

@event.listens_for(Room, "before_delete")
def delete_active_room(mapper, connection, target):
    active_room = select(func.count(Booking.id)).where(Booking.room_id == target.id,
                                        Booking.date_out >= date.today(),
                                        Booking.status != "cancelled")
    result = connection.execute(active_room)
    count = result.scalar()
    if count> 0:
        logger.warning("Попытка удаления активной комнаты")
        raise ValueError("Нельзя удалить активную комнату")

@event.listens_for(Booking, "after_insert")
def log_info(mapper, connection, target):
    logger.info(f"Бронь: #{target.id}\n"
          f"комната: {target.room_id}\n"
          f"даты: {target.date_in} - {target.date_out}\n"
          f"Цена: {target.total_price}\n")

@event.listens_for(Room, "after_insert")
def log_room(mapper, connection, target):
    logger.info(f"Создана комната: #{target.id}\n"
                f"Номер: {target.room_number}\n"
                f"Стоимость: {target.price_per_night}\n"
                f"Тип: {target.type}\n"
                f"Вместимость: {target.capacity}\n"
                f"Создана: {target.created_at}")

@event.listens_for(User, "after_delete")
def delete_user(mapper, connection, target):
    logger.info(f"Удален пользователь: #{target.id}\n"
                f"Имя: {target.full_name}\n"
                f"Почта: {target.email}\n"
                f"Телефон: {target.phone}\n"
                f"Время удаления: {datetime.now()}")

