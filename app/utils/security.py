import jwt
from datetime import datetime, timedelta
import random
from bcrypt import hashpw, gensalt, checkpw
from typing import Optional


SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Для хранения временных SMS-кодов (имитация базы)
sms_codes = {}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def send_sms_code(mobile_number: str) -> bool:
    """Генерация и отправка SMS-кода"""
    mobile_number = mobile_number.strip()
    code = random.randint(1000, 9999)
    sms_codes[mobile_number] = code
    print(f"SMS code for {mobile_number}: {code}")  # Здесь будет отправка через SMS-сервис
    return True

def verify_sms_code(mobile_number: str, code: str) -> bool:
    """Проверка SMS-кода"""
    mobile_number = mobile_number.strip() 
    return sms_codes.get(mobile_number) == int(code)

def hash_password(password: Optional[str]) -> Optional[str]:
    """Hash a password or return None if no password is provided."""
    if password is None:
        return None
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))