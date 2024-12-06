from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.request import Request  # Import Request model
from app.models.executor import Executor  # Import Executor model
from app.models.user import User  # Optional, if users create requests
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Request creation schema
class RequestCreate(BaseModel):
    title: str
    description: str
    category: str  # To determine executor group (e.g., "IT", "HR", etc.)
    user_id: Optional[int] = None  # Optional if users submit requests


@router.post("/requests", response_model=dict)
def create_request(request_data: RequestCreate, db: Session = Depends(get_db)):
    """
    Create a new request and assign it to the correct executor group based on category.
    """
    # Validate user existence (if provided)
    if request_data.user_id:
        user = db.query(User).filter(User.id == request_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    # Create the new request
    new_request = Request(
        title=request_data.title,
        description=request_data.description,
        category=request_data.category,
        user_id=request_data.user_id,
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # Assign executors to the request based on their roles
    executors = db.query(Executor).filter(Executor.role == request_data.category).all()
    if not executors:
        raise HTTPException(status_code=404, detail="No executors found for the specified category")

    # Notify executors or handle logic for executor group assignment
    assigned_executors = [{"id": executor.id, "name": executor.name} for executor in executors]

    # Return the created request with assigned executors
    return {
        "request_id": new_request.id,
        "title": new_request.title,
        "category": new_request.category,
        "assigned_executors": assigned_executors,
    }


@router.get("/requests/{request_id}", response_model=dict)
def get_request(request_id: int, db: Session = Depends(get_db)):
    """
    Fetch a request by ID and include assigned executor information.
    """
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Fetch executors assigned to this category
    executors = db.query(Executor).filter(Executor.role == request.category).all()
    executor_info = [{"id": executor.id, "name": executor.name} for executor in executors]

    return {
        "id": request.id,
        "title": request.title,
        "description": request.description,
        "category": request.category,
        "user_id": request.user_id,
        "assigned_executors": executor_info,
    }


@router.get("/requests", response_model=List[dict])
def list_requests(db: Session = Depends(get_db)):
    """
    List all requests with their assigned executors.
    """
    requests = db.query(Request).all()
    response = []
    for req in requests:
        executors = db.query(Executor).filter(Executor.role == req.category).all()
        executor_info = [{"id": executor.id, "name": executor.name} for executor in executors]

        response.append({
            "id": req.id,
            "title": req.title,
            "description": req.description,
            "category": req.category,
            "user_id": req.user_id,
            "assigned_executors": executor_info,
        })

    return response
