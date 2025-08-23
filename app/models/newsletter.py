from sqlalchemy import (
    Column,
    String,
    DateTime,
    JSON,
    Text,
    ForeignKey,
    Enum,
    Integer,
    Float,
)
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


class NewsletterType(enum.Enum):
    AUTOMATED = "automated"
    MANUAL = "manual"
    CUSTOM_PROMPT = "custom_prompt"


class Newsletter(Base):
    __tablename__ = "newsletters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Blog-style content structure
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    introduction = Column(Text, nullable=True)
    main_content = Column(Text, nullable=True)  # Structured blog content
    conclusion = Column(Text, nullable=True)

    # Content sections (JSON structure for blog sections)
    content_sections = Column(
        JSON, default=list
    )  # [{"type": "section", "title": "...", "content": "..."}]

    # Formatted content
    html_content = Column(Text, nullable=True)
    plain_text_content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    # Newsletter metadata
    status = Column(Enum(NewsletterStatus), default=NewsletterStatus.DRAFT)
    newsletter_type = Column(Enum(NewsletterType), default=NewsletterType.AUTOMATED)
    word_count = Column(Integer, default=0)
    estimated_read_time = Column(Integer, default=0)  # in minutes

    # Generation context
    custom_prompt = Column(Text, nullable=True)
    topics_covered = Column(JSON, default=list)  # ["tech", "ai", "startups"]
    tone_used = Column(String, nullable=True)  # "professional", "casual", "technical"
    sources_used = Column(
        JSON, default=list
    )  # [{"url": "...", "title": "...", "summary": "..."}]

    # AI generation metadata
    research_agent_data = Column(JSON, default=dict)  # Research agent execution data
    writing_agent_data = Column(JSON, default=dict)  # Writing agent execution data
    mindmap_markdown = Column(Text, nullable=True)  # Generated mindmap in markdown format
    mindmap_agent_data = Column(JSON, default=dict)  # Mindmap agent execution data
    generation_time_seconds = Column(Float, nullable=True)

    # Timestamps
    generated_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Email metadata
    subject_line = Column(String, nullable=True)
    email_template_used = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="newsletters")
    history_entries = relationship(
        "NewsletterHistory", back_populates="newsletter", cascade="all, delete-orphan"
    )
