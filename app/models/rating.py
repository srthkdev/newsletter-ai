"""
Newsletter Rating Model
Tracks user feedback and ratings for newsletters to improve future recommendations
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class NewsletterRating(Base):
    """Newsletter rating and feedback model"""
    
    __tablename__ = "newsletter_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    newsletter_id = Column(String(255), nullable=False, index=True)
    
    # Rating scores (1-5 scale)
    overall_rating = Column(Integer, nullable=False)  # 1-5 stars
    content_quality = Column(Integer, nullable=True)  # 1-5 quality rating
    relevance_score = Column(Integer, nullable=True)  # 1-5 relevance rating
    readability_score = Column(Integer, nullable=True)  # 1-5 readability rating
    
    # Detailed feedback
    feedback_text = Column(Text, nullable=True)
    liked_topics = Column(JSON, nullable=True)  # Topics user liked
    disliked_topics = Column(JSON, nullable=True)  # Topics user disliked
    suggested_topics = Column(JSON, nullable=True)  # Topics user wants to see
    
    # Behavioral feedback
    read_time_minutes = Column(Float, nullable=True)
    clicked_links = Column(JSON, nullable=True)  # URLs clicked
    shared = Column(Boolean, default=False)
    bookmarked = Column(Boolean, default=False)
    
    # Preference adjustments
    preferred_tone = Column(String(50), nullable=True)  # professional, casual, technical
    preferred_length = Column(String(50), nullable=True)  # short, medium, long
    preferred_frequency = Column(String(50), nullable=True)  # daily, weekly, etc.
    
    # Metadata
    newsletter_metadata = Column(JSON, nullable=True)  # Store newsletter context
    user_context = Column(JSON, nullable=True)  # User state when rating
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="newsletter_ratings")
    
    def __repr__(self):
        return f"<NewsletterRating(id={self.id}, user_id={self.user_id}, rating={self.overall_rating})>"
    
    def to_dict(self):
        """Convert rating to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "newsletter_id": self.newsletter_id,
            "overall_rating": self.overall_rating,
            "content_quality": self.content_quality,
            "relevance_score": self.relevance_score,
            "readability_score": self.readability_score,
            "feedback_text": self.feedback_text,
            "liked_topics": self.liked_topics,
            "disliked_topics": self.disliked_topics,
            "suggested_topics": self.suggested_topics,
            "read_time_minutes": self.read_time_minutes,
            "clicked_links": self.clicked_links,
            "shared": self.shared,
            "bookmarked": self.bookmarked,
            "preferred_tone": self.preferred_tone,
            "preferred_length": self.preferred_length,
            "preferred_frequency": self.preferred_frequency,
            "newsletter_metadata": self.newsletter_metadata,
            "user_context": self.user_context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @property
    def average_score(self):
        """Calculate average score across all rating dimensions"""
        scores = [
            self.overall_rating,
            self.content_quality,
            self.relevance_score,
            self.readability_score
        ]
        valid_scores = [s for s in scores if s is not None]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    @property
    def engagement_score(self):
        """Calculate engagement score based on behavioral signals"""
        score = 0
        
        # Base rating contribution (40%)
        if self.overall_rating:
            score += (self.overall_rating / 5.0) * 0.4
        
        # Read time contribution (20%)
        if self.read_time_minutes:
            # Assume 5 minutes is optimal read time
            read_time_score = min(1.0, self.read_time_minutes / 5.0)
            score += read_time_score * 0.2
        
        # Click engagement (20%)
        if self.clicked_links:
            click_score = min(1.0, len(self.clicked_links) / 3.0)  # 3 clicks = max score
            score += click_score * 0.2
        
        # Social signals (20%)
        social_score = 0
        if self.shared:
            social_score += 0.6
        if self.bookmarked:
            social_score += 0.4
        score += social_score * 0.2
        
        return min(1.0, score)