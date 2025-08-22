from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from app.models.newsletter import NewsletterStatus


class NewsletterBase(BaseModel):
    title: str
    content: Optional[str] = None
    html_content: Optional[str] = None
    summary: Optional[str] = None
    custom_prompt: Optional[str] = None


class NewsletterCreate(NewsletterBase):
    user_id: uuid.UUID


class NewsletterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    html_content: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[NewsletterStatus] = None


class Newsletter(NewsletterBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: NewsletterStatus
    generated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    sources_used: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True
