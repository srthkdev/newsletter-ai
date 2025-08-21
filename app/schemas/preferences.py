from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class PreferencesBase(BaseModel):
    topics: List[str] = Field(
        default_factory=list, description="List of topics user is interested in"
    )
    tone: str = Field(default="professional", description="Writing tone preference")
    frequency: str = Field(
        default="weekly", description="Newsletter delivery frequency"
    )
    custom_instructions: Optional[str] = Field(
        default=None, description="Custom instructions for content generation"
    )
    preferred_length: str = Field(
        default="medium", description="Preferred article length"
    )
    max_articles: int = Field(default=10, description="Maximum articles per newsletter")
    include_trending: bool = Field(default=True, description="Include trending topics")
    send_time: str = Field(default="09:00", description="Preferred send time")
    timezone: str = Field(default="UTC", description="User timezone")


class PreferencesCreate(PreferencesBase):
    user_id: uuid.UUID


class PreferencesUpdate(BaseModel):
    topics: Optional[List[str]] = None
    tone: Optional[str] = None
    frequency: Optional[str] = None
    custom_instructions: Optional[str] = None
    preferred_length: Optional[str] = None
    max_articles: Optional[int] = None
    include_trending: Optional[bool] = None
    send_time: Optional[str] = None
    timezone: Optional[str] = None


class Preferences(PreferencesBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class PreferenceRecommendation(BaseModel):
    type: str = Field(description="Type of recommendation")
    title: str = Field(description="Recommendation title")
    description: str = Field(description="Detailed description")
    action: str = Field(description="Suggested action")
    priority: str = Field(default="medium", description="Priority level")
    suggested_topics: Optional[List[str]] = Field(
        default=None, description="Suggested topics to add"
    )
    suggested_changes: Optional[List[str]] = Field(
        default=None, description="Suggested changes"
    )


class PreferenceAnalysis(BaseModel):
    summary: Dict[str, Any] = Field(
        default_factory=dict, description="Analysis summary"
    )
    insights: List[str] = Field(default_factory=list, description="Key insights")
    optimization_opportunities: List[str] = Field(
        default_factory=list, description="Optimization suggestions"
    )


class PreferencesResponse(BaseModel):
    success: bool
    preferences: Optional[Preferences] = None
    message: Optional[str] = None
    portia_result: Optional[Dict[str, Any]] = None


class RecommendationsResponse(BaseModel):
    success: bool
    recommendations: List[PreferenceRecommendation] = Field(default_factory=list)
    current_preferences: Optional[Dict[str, Any]] = None
    analysis_summary: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[PreferenceAnalysis] = None
    preferences: Optional[Dict[str, Any]] = None
    engagement_summary: Optional[Dict[str, Any]] = None
    reading_summary: Optional[Dict[str, Any]] = None
