from sqlalchemy import Column, Integer, String
from app.models.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    company_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    role = Column(String, nullable=False, default="client")
    location = Column(String, nullable=True)


    # Relationship to requests
    requests = relationship("Request", back_populates="user")
