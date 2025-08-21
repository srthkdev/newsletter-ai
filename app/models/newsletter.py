from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class NewsletterStatus(enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    SENT = "sent"
    FAILED = "failed"

class Newsletter(Base):
    __tablename__ = "newsletters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Content
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    html_content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    
    # Metadata
    status = Column(Enum(NewsletterStatus), default=NewsletterStatus.DRAFT)
    generated_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Generation context
    custom_prompt = Column(Text, nullable=True)
    sources_used = Column(JSON, default=list)
    
    # Relationship
    user = relationship("User", back_populates="newsletters")