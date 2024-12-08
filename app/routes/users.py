from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.user import User
from pydantic import BaseModel
from bcrypt import hashpw, gensalt
import logging


# Initialize logger
logger = logging.getLogger(__name__)

# Define the router
router = APIRouter()

# List of valid roles
valid_roles = ["client", "executor"]

# Schema for creating a user
class UserCreate(BaseModel):
    mobile_number: str
    password: str | None = None
    name: str
    email: str | None = None
    company_name: str | None = None
    role: str | None = "client"  # Default role is "client"
    location: str | None = None

@router.post("/users/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user.
    Validates input, hashes the password, and stores user in the database.
    """
    logger.info(f"Attempting to register user: {user.mobile_number}")
    
    try:
        # Check if the user already exists
        existing_user = db.query(User).filter(User.mobile_number == user.mobile_number).first()
        if existing_user:
            logger.error(f"User with mobile number {user.mobile_number} already exists.")
            raise HTTPException(status_code=400, detail="Mobile number already registered")
        
        # Hash the password if provided
        hashed_password = None
        if user.password:
            hashed_password = hashpw(user.password.encode('utf-8'), gensalt()).decode('utf-8')
            logger.info("Password hashed successfully.")

        # Validate the role
        if user.role not in valid_roles:
            logger.error(f"Invalid role provided: {user.role}")
            raise HTTPException(status_code=400, detail=f"Invalid role. Choose from {valid_roles}.")

        # Create a new user record
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

        logger.info(f"User {new_user.mobile_number} registered successfully with ID {new_user.id}.")
        return {"id": new_user.id, "mobile_number": new_user.mobile_number, "role": new_user.role}
    
    except Exception as e:
        logger.error(f"An error occurred while registering user: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred during registration")
