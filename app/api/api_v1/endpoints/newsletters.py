from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.database import get_db
from app.portia.custom_prompt_agent import custom_prompt_agent
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class CustomPromptRequest(BaseModel):
    user_id: str
    custom_prompt: str
    user_preferences: Optional[Dict[str, Any]] = None
    use_rag: bool = True
    send_immediately: bool = False


class PromptValidationRequest(BaseModel):
    prompt: str


class PromptExamplesResponse(BaseModel):
    examples: List[Dict[str, Any]]
    placeholders: List[str]


@router.get("/")
async def get_newsletters(db: Session = Depends(get_db)):
    """Get user's newsletter history"""
    # TODO: Implement newsletter history retrieval
    return {"newsletters": []}


@router.post("/generate")
async def generate_newsletter(db: Session = Depends(get_db)):
    """Generate a new newsletter"""
    # TODO: Implement newsletter generation with Portia agents
    return {"message": "Newsletter generation started"}


@router.post("/generate-custom")
async def generate_custom_newsletter(
    request: CustomPromptRequest, 
    db: Session = Depends(get_db)
):
    """Generate a newsletter from custom prompt"""
    try:
        # Process the custom prompt
        processing_result = await custom_prompt_agent.process_custom_prompt_full(
            user_id=request.user_id,
            custom_prompt=request.custom_prompt,
            user_preferences=request.user_preferences or {},
            use_rag=request.use_rag
        )
        
        if not processing_result["success"]:
            raise HTTPException(
                status_code=400, 
                detail=processing_result.get("error", "Failed to process custom prompt")
            )
        
        # TODO: Integrate with research and writing agents to generate actual newsletter
        # For now, return the processing results
        
        newsletter_data = {
            "newsletter_id": f"custom_{request.user_id}_{int(datetime.utcnow().timestamp())}",
            "title": f"Custom Newsletter: {processing_result['enhanced_prompt'][:50]}...",
            "custom_prompt": request.custom_prompt,
            "enhanced_prompt": processing_result["enhanced_prompt"],
            "research_parameters": processing_result["research_parameters"],
            "writing_guidelines": processing_result["writing_guidelines"],
            "status": "generated",
            "metadata": processing_result["processing_metadata"],
            "validation": processing_result["validation"],
            "rag_enhancement": processing_result.get("rag_enhancement"),
        }
        
        # If send_immediately is True, we would trigger the email sending here
        if request.send_immediately:
            # TODO: Integrate with email service
            newsletter_data["sent_at"] = datetime.utcnow().isoformat()
            newsletter_data["status"] = "sent"
        
        return newsletter_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/validate-prompt")
async def validate_custom_prompt(request: PromptValidationRequest):
    """Validate a custom prompt and provide feedback"""
    try:
        validation_result = await custom_prompt_agent.validate_prompt(request.prompt)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/prompt-examples")
async def get_prompt_examples() -> PromptExamplesResponse:
    """Get example prompts and placeholders for user guidance"""
    try:
        examples = await custom_prompt_agent.get_prompt_examples()
        placeholders = await custom_prompt_agent.get_prompt_placeholders()
        
        return PromptExamplesResponse(
            examples=examples,
            placeholders=placeholders
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get examples: {str(e)}")


@router.post("/enhance-prompt")
async def enhance_prompt_with_rag(
    user_id: str,
    prompt: str,
    user_preferences: Optional[Dict[str, Any]] = None
):
    """Enhance a prompt using RAG system"""
    try:
        enhancement_result = await custom_prompt_agent.enhance_prompt_with_rag(
            prompt=prompt,
            user_id=user_id,
            user_preferences=user_preferences or {}
        )
        return enhancement_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")


@router.post("/send-now")
async def send_newsletter_now(db: Session = Depends(get_db)):
    """Generate and send newsletter immediately"""
    # TODO: Implement immediate newsletter generation and sending
    return {"message": "Newsletter sent"}


@router.get("/{newsletter_id}")
async def get_newsletter(newsletter_id: str, db: Session = Depends(get_db)):
    """Get specific newsletter"""
    # TODO: Implement newsletter retrieval
    return {"newsletter_id": newsletter_id}


@router.get("/analytics/{user_id}")
async def get_user_analytics(user_id: str):
    """Get user's newsletter analytics and RAG insights"""
    from app.services.rag_system import rag_system
    
    try:
        # Get user preference analysis from RAG system
        analysis = await rag_system.analyze_user_preferences(user_id)
        
        # Get content recommendations
        recommendations = await rag_system.get_content_recommendations(
            user_id=user_id,
            current_topics=["technology", "business"],  # Default topics
            current_articles=[]
        )
        
        return {
            "user_id": user_id,
            "analysis": analysis,
            "recommendations": recommendations,
            "rag_status": "active"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


@router.post("/test-rag")
async def test_rag_system(user_id: str, query: str):
    """Test RAG system with similarity search"""
    from app.services.rag_system import rag_system
    
    try:
        # Test similarity search
        similar_newsletters = await rag_system.retrieve_similar_newsletters(
            user_id=user_id,
            query=query,
            top_k=5,
            similarity_threshold=0.5
        )
        
        # Test content recommendations
        recommendations = await rag_system.get_content_recommendations(
            user_id=user_id,
            current_topics=query.split(),
            current_articles=[]
        )
        
        return {
            "query": query,
            "similar_newsletters": similar_newsletters,
            "recommendations": recommendations,
            "rag_system_status": "functional"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG test failed: {str(e)}")


@router.post("/embed-test-content")
async def embed_test_content(user_id: str):
    """Embed test newsletter content for RAG testing"""
    from app.services.rag_system import rag_system
    import uuid
    
    try:
        # Create test newsletter data
        test_newsletter = {
            "title": "AI Technology Weekly - Test Newsletter",
            "content": "This week in AI: Major breakthroughs in machine learning, new OpenAI developments, and startup funding news. Key topics include neural networks, natural language processing, and computer vision advances.",
            "metadata": {
                "user_preferences": {
                    "topics": ["technology", "artificial intelligence"],
                    "tone": "professional"
                },
                "article_count": 5,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        newsletter_id = f"test_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Embed and store
        success = await rag_system.embed_and_store_newsletter(
            newsletter_id=newsletter_id,
            user_id=user_id,
            newsletter_data=test_newsletter
        )
        
        return {
            "success": success,
            "newsletter_id": newsletter_id,
            "message": "Test content embedded successfully" if success else "Embedding failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding test failed: {str(e)}")


@router.get("/scheduler/status")
async def get_scheduler_status():
    """Get newsletter scheduler status"""
    from app.services.scheduler import newsletter_scheduler
    
    try:
        status = await newsletter_scheduler.get_scheduler_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")


@router.post("/scheduler/add-user")
async def add_user_to_scheduler(
    user_id: str,
    frequency: str,
    send_time: str = "09:00",
    timezone: str = "UTC"
):
    """Add user to newsletter scheduler"""
    from app.services.scheduler import newsletter_scheduler
    
    try:
        await newsletter_scheduler.add_user_schedule(user_id, frequency, send_time, timezone)
        return {"message": f"User {user_id} added to scheduler with {frequency} frequency"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add user to scheduler: {str(e)}")


@router.delete("/scheduler/remove-user/{user_id}")
async def remove_user_from_scheduler(user_id: str):
    """Remove user from newsletter scheduler"""
    from app.services.scheduler import newsletter_scheduler
    
    try:
        await newsletter_scheduler.remove_user_schedule(user_id)
        return {"message": f"User {user_id} removed from scheduler"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove user from scheduler: {str(e)}")


@router.post("/scheduler/pause-user/{user_id}")
async def pause_user_schedule(user_id: str):
    """Pause user's newsletter schedule"""
    from app.services.scheduler import newsletter_scheduler
    
    try:
        await newsletter_scheduler.pause_user_schedule(user_id)
        return {"message": f"Schedule paused for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pause user schedule: {str(e)}")


@router.post("/scheduler/resume-user/{user_id}")
async def resume_user_schedule(user_id: str):
    """Resume user's newsletter schedule"""
    from app.services.scheduler import newsletter_scheduler
    
    try:
        await newsletter_scheduler.resume_user_schedule(user_id)
        return {"message": f"Schedule resumed for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume user schedule: {str(e)}")


@router.get("/scheduler/user/{user_id}")
async def get_user_schedule_info(user_id: str):
    """Get schedule information for a specific user"""
    from app.services.scheduler import newsletter_scheduler
    
    try:
        schedule_info = await newsletter_scheduler.get_user_schedule_info(user_id)
        if schedule_info:
            return schedule_info
        else:
            raise HTTPException(status_code=404, detail="User not found in scheduler")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user schedule: {str(e)}")


@router.post("/scheduler/trigger-immediate/{user_id}")
async def trigger_immediate_newsletter(user_id: str):
    """Trigger an immediate newsletter for a user"""
    from app.services.scheduler import newsletter_scheduler
    
    try:
        result = await newsletter_scheduler.trigger_immediate_newsletter(user_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger immediate newsletter: {str(e)}")


# Portia Agent Monitoring Endpoints
@router.get("/monitoring/dashboard")
async def get_portia_monitoring_dashboard():
    """Get comprehensive Portia agent monitoring dashboard"""
    from app.services.monitoring import get_monitoring_dashboard
    
    try:
        dashboard_data = await get_monitoring_dashboard()
        return {
            "success": True,
            "dashboard": dashboard_data
        }
    except Exception as e:
        logger.error(f"Failed to get monitoring dashboard: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/monitoring/agent/{agent_name}")
async def get_portia_agent_report(agent_name: str):
    """Get detailed performance report for specific Portia agent"""
    from app.services.monitoring import get_agent_performance_report
    
    try:
        report = await get_agent_performance_report(agent_name)
        if report:
            return {
                "success": True,
                "report": report
            }
        else:
            return {
                "success": False,
                "error": f"Agent {agent_name} not found"
            }
    except Exception as e:
        logger.error(f"Failed to get agent report: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/monitoring/start")
async def start_monitoring_system():
    """Start the Portia agent monitoring system"""
    from app.services.monitoring import start_portia_monitoring
    
    try:
        await start_portia_monitoring()
        return {
            "success": True,
            "message": "Monitoring system started successfully"
        }
    except Exception as e:
        logger.error(f"Failed to start monitoring: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/monitoring/stop")
async def stop_monitoring_system():
    """Stop the Portia agent monitoring system"""
    from app.services.monitoring import stop_portia_monitoring
    
    try:
        await stop_portia_monitoring()
        return {
            "success": True,
            "message": "Monitoring system stopped successfully"
        }
    except Exception as e:
        logger.error(f"Failed to stop monitoring: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/monitoring/resolve-error/{error_index}")
async def resolve_monitoring_error(error_index: int):
    """Mark a monitoring error as resolved"""
    from app.services.monitoring import portia_monitor
    
    try:
        success = await portia_monitor.resolve_error(error_index)
        if success:
            return {
                "success": True,
                "message": f"Error {error_index} marked as resolved"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to resolve error {error_index}"
            }
    except Exception as e:
        logger.error(f"Failed to resolve error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/monitoring/health")
async def get_system_health():
    """Get overall system health status"""
    from app.services.monitoring import get_monitoring_dashboard
    
    try:
        dashboard_data = await get_monitoring_dashboard()
        system_health = dashboard_data.get("system_health", {})
        
        return {
            "success": True,
            "health": {
                "status": system_health.get("status", "unknown"),
                "score": system_health.get("overall_score", 0),
                "monitoring_active": system_health.get("monitoring_active", False),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        return {
            "success": False,
            "error": str(e),
            "health": {
                "status": "error",
                "score": 0,
                "monitoring_active": False,
                "timestamp": datetime.utcnow().isoformat()
            }
        }


@router.get("/monitoring/agents")
async def get_all_agents_status():
    """Get status of all Portia agents"""
    from app.services.monitoring import get_monitoring_dashboard
    
    try:
        dashboard_data = await get_monitoring_dashboard()
        agents = dashboard_data.get("agents", {})
        
        return {
            "success": True,
            "agents": agents,
            "agent_count": len(agents),
            "healthy_agents": sum(1 for agent in agents.values() if agent.get("status") == "healthy"),
            "warning_agents": sum(1 for agent in agents.values() if agent.get("status") == "warning"),
            "error_agents": sum(1 for agent in agents.values() if agent.get("status") == "error")
        }
    except Exception as e:
        logger.error(f"Failed to get agents status: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Newsletter Rating Endpoints
@router.post("/rate")
async def rate_newsletter(
    user_id: str,
    newsletter_id: str,
    rating: int,
    feedback: str = None
):
    """Quick rate a newsletter with stars and optional feedback"""
    from app.services.rating_service import rating_service
    from app.schemas.rating import NewsletterRatingCreate
    
    try:
        rating_data = NewsletterRatingCreate(
            newsletter_id=newsletter_id,
            overall_rating=rating,
            feedback_text=feedback
        )
        
        created_rating = await rating_service.create_rating(
            user_id=user_id,
            rating_data=rating_data
        )
        
        return {
            "success": True,
            "rating_id": created_rating.id,
            "message": "Newsletter rated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to rate newsletter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rate-detailed")
async def rate_newsletter_detailed(
    user_id: str,
    rating_data: dict
):
    """Create detailed newsletter rating with full feedback"""
    from app.services.rating_service import rating_service
    from app.schemas.rating import NewsletterRatingCreate
    
    try:
        # Validate and create rating
        rating_create = NewsletterRatingCreate(**rating_data)
        
        created_rating = await rating_service.create_rating(
            user_id=user_id,
            rating_data=rating_create
        )
        
        return {
            "success": True,
            "rating": created_rating.to_dict(),
            "engagement_score": created_rating.engagement_score,
            "message": "Detailed rating created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create detailed rating: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ratings/{user_id}")
async def get_user_ratings(user_id: str, limit: int = 20):
    """Get user's rating history"""
    from app.services.rating_service import rating_service
    
    try:
        ratings = await rating_service.get_user_ratings(user_id, limit)
        
        return {
            "success": True,
            "ratings": [rating.to_dict() for rating in ratings],
            "count": len(ratings)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user ratings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rating-stats/{user_id}")
async def get_user_rating_stats(user_id: str):
    """Get comprehensive rating statistics for user"""
    from app.services.rating_service import rating_service
    
    try:
        stats = await rating_service.get_rating_stats(user_id)
        
        return {
            "success": True,
            "stats": stats.dict()
        }
        
    except Exception as e:
        logger.error(f"Failed to get rating stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rating-analytics/{user_id}")
async def get_user_rating_analytics(user_id: str):
    """Get advanced rating analytics and insights"""
    from app.services.rating_service import rating_service
    
    try:
        analytics = await rating_service.get_rating_analytics(user_id)
        
        return {
            "success": True,
            "analytics": analytics.dict()
        }
        
    except Exception as e:
        logger.error(f"Failed to get rating analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn-preferences/{user_id}")
async def learn_preferences_from_ratings(user_id: str):
    """Trigger preference learning from user's rating history"""
    from app.services.rating_service import rating_service
    
    try:
        result = await rating_service.learn_preferences_from_ratings(user_id)
        
        return {
            "success": True,
            "learning_result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to learn preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rating/{user_id}/{newsletter_id}")
async def get_newsletter_rating(user_id: str, newsletter_id: str):
    """Get specific newsletter rating"""
    from app.services.rating_service import rating_service
    
    try:
        rating = await rating_service.get_newsletter_rating(user_id, newsletter_id)
        
        if rating:
            return {
                "success": True,
                "rating": rating.to_dict()
            }
        else:
            return {
                "success": False,
                "message": "Rating not found"
            }
        
    except Exception as e:
        logger.error(f"Failed to get newsletter rating: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rating/{rating_id}")
async def update_newsletter_rating(
    rating_id: int,
    rating_data: dict
):
    """Update an existing newsletter rating"""
    from app.services.rating_service import rating_service
    from app.schemas.rating import NewsletterRatingUpdate
    
    try:
        rating_update = NewsletterRatingUpdate(**rating_data)
        
        updated_rating = await rating_service.update_rating(rating_id, rating_update)
        
        if updated_rating:
            return {
                "success": True,
                "rating": updated_rating.to_dict(),
                "message": "Rating updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Rating not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update rating: {e}")
        raise HTTPException(status_code=500, detail=str(e))
