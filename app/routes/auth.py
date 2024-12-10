from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.models.database import get_db
from app.crud.user_crud import UserCRUD
from app.utils.security import create_access_token, verify_sms_code, send_sms_code, hash_password
from app.utils.dependencies import get_current_user, require_admin

router = APIRouter()

# Role constants
ALLOWED_ROLES = ["client", "executor", "admin", "pending_admin"]  # Add pending_admin
SECURE_ADMIN_KEY = "key2024"  # Replace with a secure, configurable key.

# Schemas
class UserRegister(BaseModel):
    mobile_number: str
    password: Optional[str] = None
    name: str
    email: Optional[str] = None
    company_name: Optional[str] = None
    role: Optional[str] = "client"
    location: Optional[str] = None

class LoginRequest(BaseModel):
    mobile_number: str
    sms_code: str

@router.post("/register", response_model=dict)
def register_user(
    user: UserRegister,
    admin_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    If registering as admin, admin_key is required.
    """
    existing_user = UserCRUD.get_user(db, mobile_number=user.mobile_number)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Validate role
    if user.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed roles: {ALLOWED_ROLES}")

    # Handle admin registration
    approved_role = user.role
    if user.role == "admin":
        if admin_key != SECURE_ADMIN_KEY:
            approved_role = "pending_admin"

    # Hash the password
    hashed_password = hash_password(user.password)

    # Create the user
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

@router.patch("/approve-admin/{user_id}", response_model=dict)
def approve_admin(
    user_id: int,
    admin_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Approve a pending admin. Only accessible by current admins.
    """
    user = UserCRUD.get_user(db, user_id=user_id)
    if not user or user.role != "pending_admin":
        raise HTTPException(status_code=404, detail="Pending admin not found")
    
    user.role = "admin"
    db.commit()
    db.refresh(user)
    return {"detail": f"User {user_id} promoted to admin."}

# Other existing routes (send-sms, login, etc.)


@router.post("/login", response_model=dict)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Вход с помощью SMS-кода.
    """
    user = UserCRUD.get_user(db, mobile_number=request.mobile_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_sms_code(user.mobile_number, request.sms_code):
        raise HTTPException(status_code=403, detail="Invalid SMS code")
    
    token = create_access_token({"sub": user.mobile_number, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/send-sms", response_model=dict)
def send_sms(mobile_number: str):
    """
    Отправка SMS-кода пользователю.
    """
    if not send_sms_code(mobile_number):
        raise HTTPException(status_code=500, detail="Failed to send SMS")
    return {"detail": "SMS sent successfully"}

@router.get("/profile", response_model=dict)
def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Получить профиль текущего пользователя.
    """
    return {"mobile_number": current_user["sub"], "role": current_user["role"]}

@router.get("/admin-only", response_model=dict)
def admin_only_route(admin_user: dict = Depends(require_admin)):
    """
    Пример маршрута, доступного только для администраторов.
    """
    return {"message": "Welcome, Admin!"}
