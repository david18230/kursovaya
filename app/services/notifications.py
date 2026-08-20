from loguru import logger
import asyncio

async def send_booking_notification(user_id, booking_id):
    await asyncio.sleep(5)
    logger.info(f"Уведомление отправлено {user_id} о брони #{booking_id}")
async def send_welcome_notification(user_id, email):
    await asyncio.sleep(5)
    logger.info(f"Приветственное письмо отправлено на {email}")
async def send_payment_congirmation(booking_id, user_id):
    await asyncio.sleep(5)
    logger.info(f"Подтверждение оплаты брони #{booking_id} для пользователя #{user_id}")


