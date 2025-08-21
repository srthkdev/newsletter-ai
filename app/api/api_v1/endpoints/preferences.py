from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import uuid
from app.core.database import get_db
from app.models.preferences import UserPreferences
from app.models.user import User
from app.schemas.preferences import PreferencesCreate, PreferencesUpdate, Preferences
from app.portia.preference_agent import preference_agent

router = APIRouter()


@router.get("/{user_id}")
async def get_preferences(user_id: str, db: Session = Depends(get_db)):
    """Get user preferences"""
    try:
        # Convert string to UUID
        user_uuid = uuid.UUID(user_id) if user_id != "demo_user" else uuid.uuid4()

        # Get preferences from database
        preferences = (
            db.query(UserPreferences)
            .filter(UserPreferences.user_id == user_uuid)
            .first()
        )

        if preferences:
            return {
                "id": str(preferences.id),
                "user_id": str(preferences.user_id),
                "topics": preferences.topics or [],
                "tone": preferences.tone,
                "frequency": preferences.frequency,
                "custom_instructions": preferences.custom_instructions,
                "max_articles": preferences.max_articles,
                "include_trending": preferences.include_trending,
                "preferred_length": preferences.preferred_length,
                "send_time": preferences.preferred_send_time,
                "timezone": preferences.timezone,
                "created_at": preferences.created_at.isoformat()
                if preferences.created_at
                else None,
                "updated_at": preferences.updated_at.isoformat()
                if preferences.updated_at
                else None,
            }
        else:
            # Return default preferences if none exist
            return {
                "user_id": user_id,
                "topics": ["Technology", "Business"],
                "tone": "professional",
                "frequency": "weekly",
                "custom_instructions": "",
                "max_articles": 10,
                "include_trending": True,
                "preferred_length": "medium",
                "send_time": "09:00",
                "timezone": "UTC",
                "is_default": True,
            }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving preferences: {str(e)}"
        )


@router.put("/{user_id}")
async def update_preferences(
    user_id: str, preferences_data: Dict[str, Any], db: Session = Depends(get_db)
):
    """Update user preferences"""
    try:
        # Convert string to UUID
        user_uuid = uuid.UUID(user_id) if user_id != "demo_user" else uuid.uuid4()

        # Use Portia preference agent to validate and process preferences
        context = {
            "user_id": str(user_uuid),
            "action": "update",
            "preferences": preferences_data,
        }

        # Execute preference update through Portia agent
        result = await preference_agent.execute_task("update_preferences", context)

        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to update preferences"),
            )

        # Get or create preferences record
        preferences = (
            db.query(UserPreferences)
            .filter(UserPreferences.user_id == user_uuid)
            .first()
        )

        if not preferences:
            # Create new preferences record
            preferences = UserPreferences(
                user_id=user_uuid,
                topics=preferences_data.get("topics", []),
                tone=preferences_data.get("tone", "professional"),
                frequency=preferences_data.get("frequency", "weekly"),
                custom_instructions=preferences_data.get("custom_instructions", ""),
                max_articles_per_newsletter=preferences_data.get("max_articles", 10),
                preferred_length=preferences_data.get("preferred_length", "medium"),
                preferred_send_time=preferences_data.get("send_time", "09:00"),
                timezone=preferences_data.get("timezone", "UTC"),
                include_summaries=True,
                include_links=True,
                include_images=preferences_data.get("include_images", False),
                personalization_enabled=True,
            )
            db.add(preferences)
        else:
            # Update existing preferences
            preferences.topics = preferences_data.get("topics", preferences.topics)
            preferences.tone = preferences_data.get("tone", preferences.tone)
            preferences.frequency = preferences_data.get(
                "frequency", preferences.frequency
            )
            preferences.custom_instructions = preferences_data.get(
                "custom_instructions", preferences.custom_instructions
            )
            preferences.max_articles_per_newsletter = preferences_data.get(
                "max_articles", preferences.max_articles_per_newsletter
            )
            preferences.preferred_length = preferences_data.get(
                "preferred_length", preferences.preferred_length
            )
            preferences.preferred_send_time = preferences_data.get(
                "send_time", preferences.preferred_send_time
            )
            preferences.timezone = preferences_data.get(
                "timezone", preferences.timezone
            )
            preferences.include_trending = preferences_data.get(
                "include_trending", preferences.include_trending
            )

        db.commit()
        db.refresh(preferences)

        return {
            "success": True,
            "message": "Preferences updated successfully",
            "preferences": {
                "id": str(preferences.id),
                "user_id": str(preferences.user_id),
                "topics": preferences.topics,
                "tone": preferences.tone,
                "frequency": preferences.frequency,
                "custom_instructions": preferences.custom_instructions,
                "max_articles": preferences.max_articles_per_newsletter,
                "preferred_length": preferences.preferred_length,
                "send_time": preferences.preferred_send_time,
                "timezone": preferences.timezone,
                "include_trending": preferences.include_trending,
            },
            "portia_result": result,
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating preferences: {str(e)}"
        )


@router.get("/{user_id}/recommendations")
async def get_preference_recommendations(user_id: str, db: Session = Depends(get_db)):
    """Get AI-powered preference recommendations"""
    try:
        # Convert string to UUID
        user_uuid = uuid.UUID(user_id) if user_id != "demo_user" else uuid.uuid4()

        # Use Portia preference agent to generate recommendations
        context = {"user_id": str(user_uuid), "action": "recommend"}

        result = await preference_agent.execute_task("recommend_preferences", context)

        if result.get("success", False):
            return {
                "success": True,
                "recommendations": result.get("recommendations", []),
                "current_preferences": result.get("current_preferences", {}),
                "analysis_summary": result.get("analysis_summary", {}),
            }
        else:
            # Return default recommendations if agent fails
            return {
                "success": True,
                "recommendations": [
                    {
                        "type": "setup",
                        "title": "Complete Your Profile",
                        "description": "Add more topics to get better personalized content",
                        "action": "add_topics",
                        "priority": "medium",
                        "suggested_topics": [
                            "Artificial Intelligence",
                            "Innovation",
                            "Productivity",
                        ],
                    },
                    {
                        "type": "engagement",
                        "title": "Optimize Your Schedule",
                        "description": "Weekly frequency works well for most users",
                        "action": "maintain_frequency",
                        "priority": "low",
                    },
                ],
                "current_preferences": {},
                "analysis_summary": {"status": "limited_data"},
            }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting recommendations: {str(e)}"
        )


@router.post("/{user_id}/analyze")
async def analyze_preferences(user_id: str, db: Session = Depends(get_db)):
    """Analyze user preferences and behavior"""
    try:
        # Convert string to UUID
        user_uuid = uuid.UUID(user_id) if user_id != "demo_user" else uuid.uuid4()

        # Use Portia preference agent to analyze preferences
        context = {"user_id": str(user_uuid), "action": "analyze"}

        result = await preference_agent.execute_task("analyze_preferences", context)

        return {
            "success": result.get("success", False),
            "analysis": result.get("analysis", {}),
            "preferences": result.get("preferences", {}),
            "engagement_summary": result.get("engagement_summary", {}),
            "reading_summary": result.get("reading_summary", {}),
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing preferences: {str(e)}"
        )


@router.post("/topics")
async def update_topics(
    topics: List[str], user_id: str = "demo_user", db: Session = Depends(get_db)
):
    """Update user topic preferences"""
    try:
        # Convert string to UUID
        user_uuid = uuid.UUID(user_id) if user_id != "demo_user" else uuid.uuid4()

        # Get existing preferences
        preferences = (
            db.query(UserPreferences)
            .filter(UserPreferences.user_id == user_uuid)
            .first()
        )

        if preferences:
            preferences.topics = topics
            db.commit()
            db.refresh(preferences)
        else:
            # Create new preferences with just topics
            preferences = UserPreferences(user_id=user_uuid, topics=topics)
            db.add(preferences)
            db.commit()
            db.refresh(preferences)

        return {
            "success": True,
            "topics": topics,
            "message": "Topics updated successfully",
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating topics: {str(e)}")


@router.post("/tone")
async def update_tone(
    tone: str, user_id: str = "demo_user", db: Session = Depends(get_db)
):
    """Update user tone preference"""
    try:
        # Validate tone
        valid_tones = ["professional", "casual", "technical"]
        if tone not in valid_tones:
            raise HTTPException(
                status_code=400, detail=f"Invalid tone. Must be one of: {valid_tones}"
            )

        # Convert string to UUID
        user_uuid = uuid.UUID(user_id) if user_id != "demo_user" else uuid.uuid4()

        # Get existing preferences
        preferences = (
            db.query(UserPreferences)
            .filter(UserPreferences.user_id == user_uuid)
            .first()
        )

        if preferences:
            preferences.tone = tone
            db.commit()
            db.refresh(preferences)
        else:
            # Create new preferences with just tone
            preferences = UserPreferences(user_id=user_uuid, tone=tone)
            db.add(preferences)
            db.commit()
            db.refresh(preferences)

        return {"success": True, "tone": tone, "message": "Tone updated successfully"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating tone: {str(e)}")
