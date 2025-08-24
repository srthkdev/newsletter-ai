from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.auth_deps import get_current_user_from_token, get_current_user_id
from app.models.user import User
from app.portia.custom_prompt_agent import custom_prompt_agent
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


def create_formatted_content(newsletter_obj: Dict[str, Any]) -> str:
    """Create formatted newsletter content from newsletter object for beautiful display"""
    if newsletter_obj is None:
        return "Content not available."
    
    if not isinstance(newsletter_obj, dict):
        return f"Invalid content format: {type(newsletter_obj)}"
    
    content_parts = []
    
    # Add introduction with proper formatting
    introduction = newsletter_obj.get("introduction")
    if introduction:
        content_parts.append(f"## Introduction\n\n{introduction}\n\n")
    
    # Add sections with enhanced formatting
    sections = newsletter_obj.get("sections", [])
    if sections and isinstance(sections, list):
        for section_idx, section in enumerate(sections):
            if isinstance(section, dict):
                # Add section title if available
                section_title = section.get("title", f"Section {section_idx + 1}")
                content_parts.append(f"## {section_title}\n\n")
                
                # Add articles in this section with better formatting
                articles = section.get("articles", [])
                if articles and isinstance(articles, list):
                    for i, article in enumerate(articles):
                        if isinstance(article, dict):
                            # Handle structured article objects
                            title = article.get("title", f"Article {i+1}")
                            content = article.get("content", "")
                            url = article.get("url", "")
                            summary = article.get("summary", "")
                            
                            content_parts.append(f"### {title}\n\n")
                            
                            # Add summary if available
                            if summary:
                                content_parts.append(f"**Summary:** {summary}\n\n")
                            
                            if content:
                                # Keep full content for detailed view
                                content_parts.append(f"{content}\n\n")
                            
                            if url:
                                content_parts.append(f"[Read full article →]({url})\n\n")
                                
                        elif isinstance(article, str):
                            # Handle string articles from writing agent (already formatted)
                            content_parts.append(f"{article}\n\n")
                        else:
                            # Fallback for any other type
                            content_parts.append(f"{str(article)}\n\n")
                
                content_parts.append("---\n\n")  # Section separator
    
    # Add conclusion with proper formatting
    conclusion = newsletter_obj.get("conclusion")
    if conclusion:
        content_parts.append(f"## Conclusion\n\n{conclusion}\n\n")
    
    # Return formatted content or fallback message
    formatted_content = "".join(content_parts)
    return formatted_content if formatted_content.strip() else "Newsletter content is being generated..."


class CustomPromptRequest(BaseModel):
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
async def get_newsletters(
    limit: int = 10, 
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get user's newsletter history"""
    try:
        from app.utils.db_utils import db_utils
        from app.models.newsletter import NewsletterStatus
        
        newsletters = db_utils.get_user_newsletters(user_id, limit)
        
        # Convert to response format
        newsletter_list = []
        for newsletter in newsletters:
            # Create formatted content for display
            formatted_content = create_formatted_content({
                "introduction": newsletter.introduction,
                "sections": newsletter.content_sections or [],
                "conclusion": newsletter.conclusion
            })
            
            newsletter_dict = {
                "id": str(newsletter.id),
                "title": newsletter.title,
                "subtitle": newsletter.subtitle,
                "status": newsletter.status.value if hasattr(newsletter.status, 'value') else str(newsletter.status),
                "created_at": newsletter.created_at.isoformat() if newsletter.created_at else None,
                "sent_at": newsletter.sent_at.isoformat() if newsletter.sent_at else None,
                "summary": newsletter.summary,
                "content": formatted_content or newsletter.main_content,  # Use formatted content or fallback
                "introduction": newsletter.introduction,
                "main_content": newsletter.main_content,
                "conclusion": newsletter.conclusion,
                "content_sections": newsletter.content_sections or [],
                "html_content": newsletter.html_content,
                "mindmap_markdown": newsletter.mindmap_markdown,  # Add mindmap data
                "mindmap_agent_data": getattr(newsletter, 'mindmap_agent_data', {}),
                "topics": getattr(newsletter, 'topics_covered', []),
                "sources_used": getattr(newsletter, 'sources_used', []),
                "word_count": getattr(newsletter, 'word_count', 0),
                "estimated_read_time": getattr(newsletter, 'estimated_read_time', 5),
                "article_count": len(getattr(newsletter, 'content_sections', [])),
                "open_rate": 85.2,  # Mock data for now - would come from email service
                "click_rate": 12.4,  # Mock data for now - would come from email service
            }
            newsletter_list.append(newsletter_dict)
        
        return {"newsletters": newsletter_list}
        
    except Exception as e:
        logger.error(f"Failed to get newsletters: {e}")
        return {"newsletters": []}


@router.post("/generate")
async def generate_newsletter(
    send_immediately: bool = False, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Generate a new newsletter"""
    try:
        from app.portia.agent_orchestrator import NewsletterAgentOrchestrator
        from app.utils.db_utils import db_utils
        from app.models.newsletter import NewsletterStatus
        import uuid
        
        user_id = str(current_user.id)
        
        # Get user preferences
        user = db_utils.get_user_with_preferences(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Initialize orchestrator
        orchestrator = NewsletterAgentOrchestrator()
        
        # Generate newsletter using AI agents
        result = await orchestrator.generate_newsletter(
            user_id=user_id,
            send_email=send_immediately,
            user_email=current_user.email if send_immediately else None
        )
        
        # Safe logging to avoid NoneType errors
        if result is not None:
            logger.info(f"Newsletter generation result: {result.keys()}")
            if 'newsletter' in result and result['newsletter'] is not None:
                newsletter_obj = result.get('newsletter')
                if newsletter_obj is not None and hasattr(newsletter_obj, 'keys'):
                    logger.info(f"Newsletter structure: {newsletter_obj.keys()}")
                elif newsletter_obj is not None:
                    logger.info(f"Newsletter object type: {type(newsletter_obj)}")
                else:
                    logger.warning("Newsletter object is None in result")
        else:
            logger.error("Newsletter generation returned None result")
            raise HTTPException(status_code=500, detail="Newsletter generation failed - no result returned")
        
        # Ensure we have a valid result dictionary
        if not isinstance(result, dict):
            logger.error(f"Newsletter generation returned invalid type: {type(result)}")
            raise HTTPException(status_code=500, detail="Newsletter generation failed - invalid result type")
        
        # Check if generation was successful
        if not result.get("success", False):
            error_msg = result.get("error", "Newsletter generation failed")
            logger.error(f"Newsletter generation failed: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Extract newsletter data from orchestrator result
        newsletter_obj = result.get("newsletter")
        if newsletter_obj is None:
            logger.error("Newsletter object is None despite successful generation")
            raise HTTPException(status_code=500, detail="Newsletter generation failed - no newsletter content returned")
        
        # Ensure newsletter_obj is a dictionary
        if not isinstance(newsletter_obj, dict):
            logger.error(f"Newsletter object is not a dictionary: {type(newsletter_obj)}")
            raise HTTPException(status_code=500, detail="Newsletter generation failed - invalid newsletter format")
        
        # Create newsletter record in database
        newsletter_data = {
            "title": newsletter_obj.get("title", "AI-Generated Newsletter"),
            "main_content": create_formatted_content(newsletter_obj),
            "html_content": newsletter_obj.get("html_content", ""),
            "summary": newsletter_obj.get("summary", newsletter_obj.get("introduction", "")[:200] + "..." if newsletter_obj.get("introduction") else "AI-generated newsletter with personalized content"),
            "mindmap_markdown": newsletter_obj.get("mindmap_markdown", ""),  # Add mindmap data
            "mindmap_svg": result.get("steps", {}).get("mindmap", {}).get("mindmap_svg", ""),  # Add SVG data
            "keywords_data": result.get("steps", {}).get("mindmap", {}).get("keywords_data", {}),  # Add keywords
            "mindmap_agent_data": result.get("steps", {}).get("mindmap", {}),  # Store mindmap generation metadata
            "status": NewsletterStatus.SENT if send_immediately else NewsletterStatus.READY,
            "content_sections": newsletter_obj.get("sections", []),
            "sources_used": result.get("articles", [])[:5],  # Store some articles as sources
            "topics_covered": newsletter_obj.get("metadata", {}).get("user_preferences", {}).get("topics", []),
            "word_count": result.get("word_count", 0),
            "estimated_read_time": result.get("estimated_read_time", 5)
        }
        
        if send_immediately:
            newsletter_data["sent_at"] = datetime.now(timezone.utc)
        
        newsletter = db_utils.create_newsletter(user_id, newsletter_data)
        
        return {
            "success": True,
            "message": "Newsletter generated successfully",
            "newsletter_id": str(newsletter.id),
            "title": newsletter.title,
            "status": newsletter.status.value if hasattr(newsletter.status, 'value') else str(newsletter.status)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate newsletter: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/generate-custom")
async def generate_custom_newsletter(
    request: CustomPromptRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Generate a newsletter from custom prompt"""
    try:
        # Use authenticated user ID instead of request user_id
        user_id = str(current_user.id)
        
        # Process the custom prompt
        processing_result = await custom_prompt_agent.process_custom_prompt_full(
            user_id=user_id,
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
            "newsletter_id": f"custom_{user_id}_{int(datetime.now(timezone.utc).timestamp())}",
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
            newsletter_data["sent_at"] = datetime.now(timezone.utc).isoformat()
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
async def send_newsletter_now(user_id: str = "demo_user", db: Session = Depends(get_db)):
    """Generate and send newsletter immediately"""
    return await generate_newsletter(user_id=user_id, send_immediately=True, db=db)


@router.get("/{newsletter_id}")
async def get_newsletter(newsletter_id: str, db: Session = Depends(get_db)):
    """Get specific newsletter with full content"""
    try:
        from app.utils.db_utils import db_utils
        
        newsletter = db_utils.get_newsletter_with_history(newsletter_id)
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found")
        
        # Create formatted content for display
        formatted_content = create_formatted_content({
            "introduction": newsletter.introduction,
            "sections": newsletter.content_sections or [],
            "conclusion": newsletter.conclusion
        })
        
        return {
            "id": str(newsletter.id),
            "title": newsletter.title,
            "subtitle": newsletter.subtitle,
            "introduction": newsletter.introduction,
            "main_content": newsletter.main_content,
            "conclusion": newsletter.conclusion,
            "content": formatted_content or newsletter.main_content,  # Formatted content for display
            "html_content": newsletter.html_content,
            "plain_text_content": newsletter.plain_text_content,
            "summary": newsletter.summary,
            "mindmap_markdown": newsletter.mindmap_markdown,  # Add mindmap data
            "mindmap_svg": getattr(newsletter, 'mindmap_svg', ''),  # Add SVG data
            "keywords_data": getattr(newsletter, 'keywords_data', {}),  # Add keywords data
            "mindmap_agent_data": getattr(newsletter, 'mindmap_agent_data', {}),
            "status": newsletter.status.value if hasattr(newsletter.status, 'value') else str(newsletter.status),
            "newsletter_type": newsletter.newsletter_type.value if hasattr(newsletter.newsletter_type, 'value') else str(newsletter.newsletter_type),
            "word_count": newsletter.word_count or 0,
            "estimated_read_time": newsletter.estimated_read_time or 5,
            "custom_prompt": newsletter.custom_prompt,
            "tone_used": newsletter.tone_used,
            "created_at": newsletter.created_at.isoformat() if newsletter.created_at else None,
            "generated_at": newsletter.generated_at.isoformat() if newsletter.generated_at else None,
            "sent_at": newsletter.sent_at.isoformat() if newsletter.sent_at else None,
            "updated_at": newsletter.updated_at.isoformat() if newsletter.updated_at else None,
            "subject_line": newsletter.subject_line,
            "email_template_used": newsletter.email_template_used,
            "content_sections": newsletter.content_sections or [],
            "topics_covered": newsletter.topics_covered or [],
            "sources_used": newsletter.sources_used or [],
            "research_agent_data": newsletter.research_agent_data or {},
            "writing_agent_data": newsletter.writing_agent_data or {},
            "generation_time_seconds": newsletter.generation_time_seconds,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get newsletter: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
    import uuid
    
    try:
        # Convert user_id to UUID if needed
        if user_id == "demo_user":
            # For demo user, create a consistent UUID
            demo_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
            user_uuid = demo_uuid
        else:
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                # If user_id is not a valid UUID, create one from the string
                import hashlib
                user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:32]
                user_uuid = uuid.UUID(user_hash[:8] + '-' + user_hash[8:12] + '-' + user_hash[12:16] + '-' + user_hash[16:20] + '-' + user_hash[20:32])
        
        rating_data = NewsletterRatingCreate(
            newsletter_id=newsletter_id,
            overall_rating=rating,
            feedback_text=feedback
        )
        
        created_rating = await rating_service.create_rating(
            user_id=str(user_uuid),
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
    import uuid
    
    try:
        # Convert user_id to UUID if needed
        if user_id == "demo_user":
            demo_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
            user_uuid = demo_uuid
        else:
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                import hashlib
                user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:32]
                user_uuid = uuid.UUID(user_hash[:8] + '-' + user_hash[8:12] + '-' + user_hash[12:16] + '-' + user_hash[16:20] + '-' + user_hash[20:32])
        
        rating = await rating_service.get_newsletter_rating(str(user_uuid), newsletter_id)
        
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
        # Return not found instead of error to avoid breaking the UI
        return {
            "success": False,
            "message": "Rating not found"
        }


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


@router.post("/mindmap/{newsletter_id}")
async def generate_newsletter_mindmap(
    newsletter_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Generate or regenerate mindmap for a specific newsletter"""
    try:
        from app.utils.db_utils import db_utils
        from app.portia.agent_orchestrator import agent_orchestrator
        
        # Get newsletter data
        newsletter = db_utils.get_newsletter_with_history(newsletter_id)
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found")
        
        # Check if user owns this newsletter
        if str(newsletter.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prepare context for mindmap generation
        mindmap_context = {
            "user_id": str(current_user.id),
            "newsletter_content": {
                "title": newsletter.title,
                "introduction": newsletter.introduction,
                "sections": newsletter.content_sections or [],
                "conclusion": newsletter.conclusion,
                "summary": newsletter.summary
            },
            "articles": newsletter.sources_used or [],
            "topics": newsletter.topics_covered or [],
            "newsletter_id": newsletter_id
        }
        
        # Generate mindmap using the mindmap agent
        mindmap_result = await agent_orchestrator.mindmap_agent.execute_task(
            "generate_mindmap", mindmap_context
        )
        
        if mindmap_result["success"]:
            # Update newsletter with new mindmap
            newsletter.mindmap_markdown = mindmap_result["mindmap_markdown"]
            newsletter.mindmap_agent_data = mindmap_result.get("metadata", {})
            
            # Save to database
            db.commit()
            
            return {
                "success": True,
                "mindmap_markdown": mindmap_result["mindmap_markdown"],
                "metadata": mindmap_result.get("metadata", {}),
                "newsletter_id": newsletter_id,
                "message": "Mindmap generated successfully"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate mindmap: {mindmap_result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate mindmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mindmap/{newsletter_id}")
async def get_newsletter_mindmap(
    newsletter_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Get mindmap for a specific newsletter"""
    try:
        from app.utils.db_utils import db_utils
        
        # Get newsletter data
        newsletter = db_utils.get_newsletter_with_history(newsletter_id)
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found")
        
        # Check if user owns this newsletter
        if str(newsletter.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "mindmap_markdown": newsletter.mindmap_markdown,
            "mindmap_agent_data": getattr(newsletter, 'mindmap_agent_data', {}),
            "newsletter_id": newsletter_id,
            "has_mindmap": bool(newsletter.mindmap_markdown)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get mindmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))
