from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.executor import Executor
from pydantic import BaseModel
from bcrypt import hashpw, gensalt

router = APIRouter()

class ExecutorCreate(BaseModel):
    mobile_number: str
    password: str | None = None
    name: str #need name
    email: str | None = None
    company_name: str | None = None
    role: str  # Mandatory field for executor roles
    group: str   # Mandatory group for executor

@router.post("/executors/register")
def register_executor(executor: ExecutorCreate, db: Session = Depends(get_db)):
    if db.query(Executor).filter(Executor.mobile_number == executor.mobile_number).first():
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    hashed_password = hashpw(executor.password.encode('utf-8'), gensalt()).decode('utf-8')
    new_executor = Executor(
        mobile_number=executor.mobile_number,
        name=executor.name,
        email=executor.email,
        company_name=executor.company_name,
        hashed_password=hashed_password,
        role=executor.role,
        group=executor.group
    )
    db.add(new_executor)
    db.commit()
    db.refresh(new_executor)
    return {"id": new_executor.id, "mobile_number": new_executor.mobile_number, "role": new_executor.role, "group": new_executor.group}
