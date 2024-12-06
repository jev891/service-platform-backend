from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

class Executor(Base):
    __tablename__ = "executors"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)  # Optional
    email = Column(String, unique=True, index=True, nullable=True)  # Optional
    company_name = Column(String, nullable=True)  # Optional
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Define specific executor roles (e.g., "tech_support", "legal_advice")
    group = Column(String, nullable=True)  # Group executor belongs to
