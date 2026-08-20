import os
import hmac
import hashlib
import bcrypt
from datetime import datetime, timedelta, timezone
from  jose import jwt, JWTError

def hash_password(password: str):
    password = password.encode("utf-8")
    salted = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salted).decode("utf-8")
    return hashed

def verify_password(password: str, hashed: str) -> bool:
    password = password.encode("utf-8")
    hashed = hashed.encode("utf-8")
    return bcrypt.checkpw(password, hashed)

ACCESS_TOKEN_EXPIRE_MINUTES = 120
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    copied_data = data.copy()
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    copied_data["exp"] = expiration_time
    token = jwt.encode(copied_data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token):
    untoken = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return untoken

def validate_password_strength(password: str)-> bool:
    if len(password) < 6:
        return False
    has_digit = any(c.isdigit() for c in password)
    has_letter = any(c.isalpha() for c in password)
    return has_digit and has_letter
