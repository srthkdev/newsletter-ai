from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Session and authentication
    session_token = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    newsletters = relationship("Newsletter", back_populates="user")