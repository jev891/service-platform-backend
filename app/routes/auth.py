from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.models.database import get_db
from app.crud.user_crud import UserCRUD
from app.utils.security import create_access_token, verify_sms_code, send_sms_code, hash_password


router = APIRouter()

# Role constants
ALLOWED_ROLES = ["client", "executor", "admin"]

# Схемы для регистрации и входа
class UserRegister(BaseModel):
    mobile_number: str
    password: Optional[str] = None
    name: str
    email: Optional[str] = None
    company_name: Optional[str] = None
    role: Optional[str] = "client"  # Default role is "client"
    location: Optional[str] = None

class LoginRequest(BaseModel):
    mobile_number: str
    sms_code: str

@router.post("/register", response_model=dict)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.
    Проверяет наличие пользователя и регистрирует нового при отсутствии.
    """
    # Проверяем, существует ли пользователь
    existing_user = UserCRUD.get_user(db, mobile_number=user.mobile_number)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Validate the role
    if user.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed roles: {ALLOWED_ROLES}")

    # Hash the password
    hashed_password = hash_password(user.password)

    # Handle admin approval
    approved_role = user.role if user.role != "admin" else "pending_admin"

    # Регистрируем нового пользователя
    new_user = UserCRUD.create_user(
        db=db,
        mobile_number=user.mobile_number,
        name=user.name,
        email=user.email,
        company_name=user.company_name,
        hashed_password=hashed_password,
        role=approved_role,
        location=user.location,
    )
    return {"id": new_user.id, "mobile_number": new_user.mobile_number, "role": new_user.role}

@router.post("/login", response_model=dict)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Вход с помощью SMS-кода.
    Проверяет код и возвращает JWT токен.
    """
    # Ищем пользователя по номеру телефона
    user = UserCRUD.get_user(db, mobile_number=request.mobile_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем SMS-код
    if not verify_sms_code(user.mobile_number, request.sms_code):
        raise HTTPException(status_code=403, detail="Invalid SMS code")
    
    # Генерируем JWT токен
    token = create_access_token({"sub": user.mobile_number, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/send-sms", response_model=dict)
def send_sms(mobile_number: str):
    """
    Отправка SMS-кода пользователю.
    """
    # Отправляем SMS-код
    if not send_sms_code(mobile_number):
        raise HTTPException(status_code=500, detail="Failed to send SMS")
    return {"detail": "SMS sent successfully"}
