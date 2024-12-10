import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
import random
from bcrypt import hashpw, gensalt, checkpw
from typing import Optional
from fastapi import HTTPException, status

# Constants
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Simulated database for SMS codes
sms_codes = {}

# Generate JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a JWT token for the given data with an optional expiration time.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Decode and validate JWT token
def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    Raises exceptions for expired or invalid tokens.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Generate SMS code
def send_sms_code(mobile_number: str) -> bool:
    """
    Generate and store an SMS code for the given mobile number.
    """
    mobile_number = mobile_number.strip()
    code = random.randint(1000, 9999)
    sms_codes[mobile_number] = code
    print(f"SMS code for {mobile_number}: {code}")  # Replace with actual SMS service integration
    return True

# Verify SMS code
def verify_sms_code(mobile_number: str, code: str) -> bool:
    """
    Validate the SMS code for a given mobile number.
    """
    mobile_number = mobile_number.strip()
    return sms_codes.get(mobile_number) == int(code)

# Hash a password
def hash_password(password: Optional[str]) -> Optional[str]:
    """
    Hash a password or return None if no password is provided.
    """
    if password is None:
        return None
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

# Verify a plain password against a hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hashed version.
    """
    return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
