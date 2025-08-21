from sqlalchemy import (
    Column,
    String,
    DateTime,
    JSON,
    Text,
    ForeignKey,
    Enum,
    Boolean,
    Integer,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class DeliveryStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"


class NewsletterHistory(Base):
    __tablename__ = "newsletter_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    newsletter_id = Column(
        UUID(as_uuid=True), ForeignKey("newsletters.id"), nullable=False
    )

    # Delivery tracking
    delivery_status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    last_clicked_at = Column(DateTime(timezone=True), nullable=True)

    # Email metadata
    email_address = Column(String, nullable=False)  # Email it was sent to
    subject_line = Column(String, nullable=True)
    message_id = Column(String, nullable=True)  # Email service message ID

    # Engagement tracking
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    time_spent_reading = Column(Integer, default=0)  # seconds

    # Delivery metadata
    email_service_used = Column(String, default="resend")  # "resend", "sendgrid", etc.
    delivery_attempts = Column(Integer, default=0)
    last_delivery_attempt = Column(DateTime(timezone=True), nullable=True)
    delivery_error = Column(Text, nullable=True)

    # User feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    user_feedback = Column(Text, nullable=True)
    marked_as_favorite = Column(Boolean, default=False)

    # Analytics data
    device_type = Column(String, nullable=True)  # "mobile", "desktop", "tablet"
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    location_data = Column(
        JSON, default=dict
    )  # {"country": "US", "city": "San Francisco"}

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="newsletter_history")
    newsletter = relationship("Newsletter", back_populates="history_entries")
