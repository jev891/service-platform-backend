from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db

from app.models.user import User         #make sure two dif form work together
from app.models.request import Request

from pydantic import BaseModel
from bcrypt import hashpw, gensalt

router = APIRouter()

class UserCreate(BaseModel):
    mobile_number: str
    password: str
    name: str
    email: str | None = None
    company_name: str | None = None
    role: str | None = "client"  # Optional; defaults to "client"

@router.post("/users/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the mobile number is already registered
    if db.query(User).filter(User.mobile_number == user.mobile_number).first():
        raise HTTPException(status_code=400, detail="Mobile number already registered")

    # Hash the password before saving
    hashed_password = hashpw(user.password.encode('utf-8'), gensalt()).decode('utf-8')

    # Validate role
    valid_roles = ["client", "executor"]
    if user.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from {valid_roles}.")

    # Create a new user
    new_user = User(
        mobile_number=user.mobile_number,
        name=user.name,
        email=user.email,
        company_name=user.company_name,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"id": new_user.id, "mobile_number": new_user.mobile_number, "role": new_user.role}
