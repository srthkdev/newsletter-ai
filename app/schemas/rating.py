"""
Newsletter Rating Schemas
Pydantic models for newsletter rating validation and serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class NewsletterRatingBase(BaseModel):
    """Base newsletter rating schema"""
    overall_rating: int = Field(..., ge=1, le=5, description="Overall rating from 1-5 stars")
    content_quality: Optional[int] = Field(None, ge=1, le=5, description="Content quality rating 1-5")
    relevance_score: Optional[int] = Field(None, ge=1, le=5, description="Content relevance rating 1-5")
    readability_score: Optional[int] = Field(None, ge=1, le=5, description="Content readability rating 1-5")
    
    feedback_text: Optional[str] = Field(None, max_length=1000, description="User feedback text")
    liked_topics: Optional[List[str]] = Field(None, description="Topics the user liked")
    disliked_topics: Optional[List[str]] = Field(None, description="Topics the user disliked")
    suggested_topics: Optional[List[str]] = Field(None, description="Topics the user wants to see")
    
    read_time_minutes: Optional[float] = Field(None, ge=0, description="Time spent reading in minutes")
    clicked_links: Optional[List[str]] = Field(None, description="URLs that were clicked")
    shared: Optional[bool] = Field(False, description="Whether the newsletter was shared")
    bookmarked: Optional[bool] = Field(False, description="Whether the newsletter was bookmarked")
    
    preferred_tone: Optional[str] = Field(None, pattern="^(professional|casual|technical)$")
    preferred_length: Optional[str] = Field(None, pattern="^(short|medium|long)$")
    preferred_frequency: Optional[str] = Field(None, pattern="^(daily|every_2_days|weekly|monthly)$")


class NewsletterRatingCreate(NewsletterRatingBase):
    """Schema for creating a new newsletter rating"""
    newsletter_id: str = Field(..., description="Newsletter identifier")
    
    @validator('feedback_text')
    def validate_feedback(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Feedback must be at least 10 characters long')
        return v.strip() if v else None
    
    @validator('liked_topics', 'disliked_topics', 'suggested_topics')
    def validate_topics(cls, v):
        if v:
            # Remove empty strings and limit to 10 topics
            clean_topics = [topic.strip() for topic in v if topic.strip()]
            return clean_topics[:10]
        return v


class NewsletterRatingUpdate(BaseModel):
    """Schema for updating an existing newsletter rating"""
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    content_quality: Optional[int] = Field(None, ge=1, le=5)
    relevance_score: Optional[int] = Field(None, ge=1, le=5)
    readability_score: Optional[int] = Field(None, ge=1, le=5)
    
    feedback_text: Optional[str] = Field(None, max_length=1000)
    liked_topics: Optional[List[str]] = None
    disliked_topics: Optional[List[str]] = None
    suggested_topics: Optional[List[str]] = None
    
    read_time_minutes: Optional[float] = Field(None, ge=0)
    clicked_links: Optional[List[str]] = None
    shared: Optional[bool] = None
    bookmarked: Optional[bool] = None
    
    preferred_tone: Optional[str] = Field(None, pattern="^(professional|casual|technical)$")
    preferred_length: Optional[str] = Field(None, pattern="^(short|medium|long)$")
    preferred_frequency: Optional[str] = Field(None, pattern="^(daily|every_2_days|weekly|monthly)$")


class NewsletterRatingResponse(NewsletterRatingBase):
    """Schema for newsletter rating response"""
    id: int
    user_id: int
    newsletter_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    average_score: float
    engagement_score: float
    newsletter_metadata: Optional[Dict[str, Any]] = None
    user_context: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class NewsletterRatingStats(BaseModel):
    """Schema for rating statistics"""
    total_ratings: int
    average_rating: float
    rating_distribution: Dict[str, int]  # "1": count, "2": count, etc.
    
    # Quality metrics
    average_content_quality: Optional[float]
    average_relevance: Optional[float]
    average_readability: Optional[float]
    average_engagement: float
    
    # Topic analysis
    most_liked_topics: List[Dict[str, Any]]  # [{"topic": str, "count": int}]
    most_disliked_topics: List[Dict[str, Any]]
    suggested_topics: List[Dict[str, Any]]
    
    # Behavioral metrics
    average_read_time: Optional[float]
    link_click_rate: float
    share_rate: float
    bookmark_rate: float
    
    # Preference insights
    preferred_tone_distribution: Dict[str, int]
    preferred_length_distribution: Dict[str, int]
    preferred_frequency_distribution: Dict[str, int]


class QuickRating(BaseModel):
    """Schema for quick rating (just stars and optional feedback)"""
    newsletter_id: str
    rating: int = Field(..., ge=1, le=5, description="Quick star rating 1-5")
    feedback: Optional[str] = Field(None, max_length=500, description="Optional quick feedback")


class RatingAnalytics(BaseModel):
    """Schema for rating analytics and insights"""
    user_id: int
    rating_summary: NewsletterRatingStats
    improvement_suggestions: List[str]
    personalization_insights: List[str]
    engagement_trends: Dict[str, Any]
    topic_preferences: Dict[str, float]  # topic -> preference score
    
    class Config:
        from_attributes = True


class BulkRatingInsights(BaseModel):
    """Schema for bulk rating analysis across users"""
    total_users_rated: int
    global_stats: NewsletterRatingStats
    top_performing_newsletters: List[Dict[str, Any]]
    common_feedback_themes: List[Dict[str, Any]]
    content_optimization_suggestions: List[str]