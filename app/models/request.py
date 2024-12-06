from sqlalchemy import Column, Integer, String, ForeignKey, Text, Time, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="open")  # Options: open, closed, pending
    budget = Column(Integer, nullable=True)
    category = Column(String, nullable=False)  # E.g., "IT", "HR"
    approximate_time_required = Column(Integer, nullable=True)  # Approximate time in hours
    help_day = Column(String, nullable=True)  # Preferred day (e.g., "Monday")
    preferred_time = Column(Time, nullable=True)  # Preferred time of day

    # Relationship to the user
    user = relationship("User", back_populates="requests")
