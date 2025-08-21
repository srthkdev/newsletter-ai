from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Newsletter preferences
    topics = Column(JSON, default=list)  # ["tech", "business", "science", etc.]
    tone = Column(String, default="professional")  # "professional", "casual", "technical"
    frequency = Column(String, default="weekly")  # "daily", "every_2_days", "weekly", "monthly"
    
    # Custom preferences
    custom_instructions = Column(String, nullable=True)
    preferred_length = Column(String, default="medium")  # "short", "medium", "long"
    
    # Relationship
    user = relationship("User", back_populates="preferences")