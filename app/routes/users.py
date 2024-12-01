from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.user import User
from pydantic import BaseModel
from bcrypt import hashpw, gensalt

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str

@router.post("/users", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before saving
    hashed_password = hashpw(user.password.encode('utf-8'), gensalt()).decode('utf-8')
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}
