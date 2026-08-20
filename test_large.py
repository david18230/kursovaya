import requests
from loguru import logger

r = requests.post('http://127.0.0.1:8000/auth/register', json={
    'full_name': 'A' * 2_000_000,
    'phone': '89991234567',
    'email': 'test@mail.ru',
    'password': '123456'
})
# print(r.status_code, r.json())
logger.patch()