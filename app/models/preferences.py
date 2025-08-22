from sqlalchemy import Column, String, JSON, ForeignKey, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Core newsletter preferences
    topics = Column(
        JSON, default=list
    )  # ["tech", "business", "science", "ai", "startups", etc.]
    tone = Column(
        String, default="professional"
    )  # "professional", "casual", "technical"
    frequency = Column(
        String, default="weekly"
    )  # "daily", "every_2_days", "weekly", "monthly"

    # Content preferences
    preferred_length = Column(String, default="medium")  # "short", "medium", "long"
    include_summaries = Column(Boolean, default=True)
    include_links = Column(Boolean, default=True)
    include_images = Column(Boolean, default=False)
    include_trending = Column(Boolean, default=False)  # Include trending topics

    # Advanced preferences
    custom_instructions = Column(String, nullable=True)
    excluded_sources = Column(JSON, default=list)  # URLs or domains to exclude
    preferred_sources = Column(JSON, default=list)  # Preferred news sources
    keywords_to_include = Column(JSON, default=list)  # Keywords to prioritize
    keywords_to_exclude = Column(JSON, default=list)  # Keywords to avoid

    # Delivery preferences
    preferred_send_time = Column(String, default="09:00")  # "HH:MM" format
    timezone = Column(String, default="UTC")
    send_on_weekends = Column(Boolean, default=True)

    # Engagement preferences
    max_articles_per_newsletter = Column(Integer, default=5)
    min_article_quality_score = Column(Integer, default=7)  # 1-10 scale

    # Personalization data (for RAG and memory)
    reading_history_weight = Column(
        Integer, default=5
    )  # 1-10, how much to weight past reading
    personalization_enabled = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_newsletter_sent = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    user = relationship("User", back_populates="preferences")
