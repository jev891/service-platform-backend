from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.user import User
from pydantic import BaseModel
from bcrypt import hashpw, gensalt
import logging
from app.utils.dependencies import get_current_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter()

valid_roles = ["client", "executor"]

class UserCreate(BaseModel):
    mobile_number: str
    password: str | None = None
    name: str
    email: str | None = None
    company_name: str | None = None
    role: str | None = "client"
    location: str | None = None

@router.post("/users/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user.
    """
    logger.info(f"Attempting to register user: {user.mobile_number}")
    
    existing_user = db.query(User).filter(User.mobile_number == user.mobile_number).first()
    if existing_user:
        logger.error(f"User with mobile number {user.mobile_number} already exists.")
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    
    hashed_password = None
    if user.password:
        hashed_password = hashpw(user.password.encode('utf-8'), gensalt()).decode('utf-8')

    if user.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from {valid_roles}.")

    new_user = User(
        mobile_number=user.mobile_number,
        name=user.name,
        email=user.email,
        company_name=user.company_name,
        hashed_password=hashed_password,
        role=user.role,
        location=user.location
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "mobile_number": new_user.mobile_number, "role": new_user.role}

@router.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, admin_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    """
    Удалить пользователя. Доступно только администраторам.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": f"User {user_id} deleted successfully"}
