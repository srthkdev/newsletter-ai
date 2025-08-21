"""
Portia AI Agent Integration Testing Endpoints
Comprehensive testing and verification of all agent integrations
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import asyncio
from datetime import datetime

from app.portia.agent_orchestrator import agent_orchestrator
from app.services.monitoring import record_agent_execution

router = APIRouter()


@router.post("/test-all-agents")
async def test_all_agent_integrations():
    """Test all Portia AI agents and their integrations"""
    
    test_results = {
        "started_at": datetime.utcnow().isoformat(),
        "tests": {},
        "overall_status": "pending",
        "summary": {}
    }
    
    try:
        # Test each agent systematically
        
        # 1. Test Research Agent
        print("🔍 Testing Research Agent...")
        research_start = datetime.utcnow()
        try:
            research_result = await agent_orchestrator.research_agent.execute_task(
                "search_by_topics",
                {
                    "user_id": "test_user",
                    "topics": ["technology", "artificial intelligence"],
                    "days_back": 2,
                    "max_results_per_topic": 3
                }
            )
            research_duration = (datetime.utcnow() - research_start).total_seconds()
            
            await record_agent_execution(
                "research_agent",
                research_duration,
                research_result.get("success", False),
                {"test": "integration_test"},
                None if research_result.get("success") else Exception(research_result.get("error", "Unknown error"))
            )
            
            test_results["tests"]["research_agent"] = {
                "status": "success" if research_result["success"] else "error",
                "duration": research_duration,
                "articles_found": len(research_result.get("articles", [])),
                "message": research_result.get("error") if not research_result["success"] else "Working correctly",
                "details": research_result
            }
        except Exception as e:
            research_duration = (datetime.utcnow() - research_start).total_seconds()
            await record_agent_execution("research_agent", research_duration, False, {"test": "integration_test"}, e)
            test_results["tests"]["research_agent"] = {
                "status": "error",
                "duration": research_duration,
                "message": str(e),
                "articles_found": 0
            }
        
        # 2. Test Writing Agent with mock articles
        print("✍️ Testing Writing Agent...")
        writing_start = datetime.utcnow()
        try:
            mock_articles = [
                {
                    "title": "AI Breakthrough in Natural Language Processing",
                    "url": "https://example.com/ai-nlp",
                    "content": "Researchers have made significant advances in NLP technology...",
                    "topic": "artificial intelligence"
                },
                {
                    "title": "New Technology Trends for 2024",
                    "url": "https://example.com/tech-trends",
                    "content": "The technology landscape is evolving rapidly with new innovations...",
                    "topic": "technology"
                }
            ]
            
            writing_result = await agent_orchestrator.writing_agent.execute_task(
                "generate_newsletter",
                {
                    "user_id": "test_user",
                    "articles": mock_articles,
                    "user_preferences": {
                        "tone": "professional",
                        "topics": ["technology", "artificial intelligence"]
                    }
                }
            )
            writing_duration = (datetime.utcnow() - writing_start).total_seconds()
            
            await record_agent_execution(
                "writing_agent",
                writing_duration,
                writing_result.get("success", False),
                {"test": "integration_test", "articles_count": len(mock_articles)},
                None if writing_result.get("success") else Exception(writing_result.get("error", "Unknown error"))
            )
            
            test_results["tests"]["writing_agent"] = {
                "status": "success" if writing_result["success"] else "error",
                "duration": writing_duration,
                "newsletter_generated": bool(writing_result.get("newsletter")),
                "word_count": writing_result.get("word_count", 0),
                "message": writing_result.get("error") if not writing_result["success"] else "Working correctly",
                "rag_context_used": writing_result.get("rag_context", {}).get("rag_available", False)
            }
        except Exception as e:
            writing_duration = (datetime.utcnow() - writing_start).total_seconds()
            await record_agent_execution("writing_agent", writing_duration, False, {"test": "integration_test"}, e)
            test_results["tests"]["writing_agent"] = {
                "status": "error",
                "duration": writing_duration,
                "message": str(e),
                "newsletter_generated": False
            }
        
        # 3. Test Preference Agent
        print("⚙️ Testing Preference Agent...")
        preference_start = datetime.utcnow()
        try:
            # Test getting preferences
            pref_result = await agent_orchestrator.preference_agent.execute_task(
                "get_preferences",
                {"user_id": "test_user"}
            )
            
            # Test updating preferences
            update_result = await agent_orchestrator.preference_agent.execute_task(
                "update_preferences",
                {
                    "user_id": "test_user",
                    "preferences": {
                        "topics": ["technology", "artificial intelligence"],
                        "tone": "professional",
                        "frequency": "weekly"
                    }
                }
            )
            
            preference_duration = (datetime.utcnow() - preference_start).total_seconds()
            success = pref_result.get("success", False) and update_result.get("success", False)
            
            await record_agent_execution(
                "preference_agent",
                preference_duration,
                success,
                {"test": "integration_test"},
                None if success else Exception("Preference operations failed")
            )
            
            test_results["tests"]["preference_agent"] = {
                "status": "success" if success else "error",
                "duration": preference_duration,
                "get_preferences": pref_result.get("success", False),
                "update_preferences": update_result.get("success", False),
                "message": "Working correctly" if success else "Failed to get/update preferences"
            }
        except Exception as e:
            preference_duration = (datetime.utcnow() - preference_start).total_seconds()
            await record_agent_execution("preference_agent", preference_duration, False, {"test": "integration_test"}, e)
            test_results["tests"]["preference_agent"] = {
                "status": "error",
                "duration": preference_duration,
                "message": str(e)
            }
        
        # 4. Test Custom Prompt Agent
        print("🎯 Testing Custom Prompt Agent...")
        prompt_start = datetime.utcnow()
        try:
            prompt_result = await agent_orchestrator.custom_prompt_agent.execute_task(
                "process_prompt",
                {
                    "user_id": "test_user",
                    "custom_prompt": "Create a newsletter about the latest AI developments with a focus on practical applications",
                    "user_preferences": {
                        "tone": "professional",
                        "topics": ["artificial intelligence"]
                    }
                }
            )
            prompt_duration = (datetime.utcnow() - prompt_start).total_seconds()
            
            await record_agent_execution(
                "custom_prompt_agent",
                prompt_duration,
                prompt_result.get("success", False),
                {"test": "integration_test"},
                None if prompt_result.get("success") else Exception(prompt_result.get("error", "Unknown error"))
            )
            
            test_results["tests"]["custom_prompt_agent"] = {
                "status": "success" if prompt_result["success"] else "error",
                "duration": prompt_duration,
                "prompt_processed": bool(prompt_result.get("enhanced_prompt")),
                "research_parameters": bool(prompt_result.get("research_parameters")),
                "writing_guidelines": bool(prompt_result.get("writing_guidelines")),
                "message": prompt_result.get("error") if not prompt_result["success"] else "Working correctly"
            }
        except Exception as e:
            prompt_duration = (datetime.utcnow() - prompt_start).total_seconds()
            await record_agent_execution("custom_prompt_agent", prompt_duration, False, {"test": "integration_test"}, e)
            test_results["tests"]["custom_prompt_agent"] = {
                "status": "error",
                "duration": prompt_duration,
                "message": str(e)
            }
        
        # 5. Test Full Orchestrator Workflow
        print("🤖 Testing Full Agent Orchestrator...")
        orchestrator_start = datetime.utcnow()
        try:
            # Test the complete workflow
            orchestrator_result = await agent_orchestrator.generate_newsletter(
                user_id="test_user",
                custom_prompt="Create a brief newsletter about technology trends",
                send_email=False  # Don't actually send email in test
            )
            orchestrator_duration = (datetime.utcnow() - orchestrator_start).total_seconds()
            
            await record_agent_execution(
                "agent_orchestrator",
                orchestrator_duration,
                orchestrator_result.get("success", False),
                {"test": "integration_test", "full_workflow": True},
                None if orchestrator_result.get("success") else Exception("Orchestrator workflow failed")
            )
            
            test_results["tests"]["agent_orchestrator"] = {
                "status": "success" if orchestrator_result["success"] else "error",
                "duration": orchestrator_duration,
                "workflow_completed": orchestrator_result.get("success", False),
                "newsletter_generated": bool(orchestrator_result.get("newsletter")),
                "steps_completed": len([s for s in orchestrator_result.get("steps", {}).values() if s.get("success")]),
                "total_steps": len(orchestrator_result.get("steps", {})),
                "message": orchestrator_result.get("error") if not orchestrator_result["success"] else "Full workflow working correctly"
            }
        except Exception as e:
            orchestrator_duration = (datetime.utcnow() - orchestrator_start).total_seconds()
            await record_agent_execution("agent_orchestrator", orchestrator_duration, False, {"test": "integration_test"}, e)
            test_results["tests"]["agent_orchestrator"] = {
                "status": "error",
                "duration": orchestrator_duration,
                "message": str(e)
            }
        
        # Calculate overall results
        total_tests = len(test_results["tests"])
        successful_tests = sum(1 for test in test_results["tests"].values() if test["status"] == "success")
        total_duration = sum(test["duration"] for test in test_results["tests"].values())
        
        test_results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "total_duration": total_duration,
            "average_duration": total_duration / total_tests if total_tests > 0 else 0
        }
        
        test_results["overall_status"] = "success" if successful_tests == total_tests else "partial" if successful_tests > 0 else "failed"
        test_results["completed_at"] = datetime.utcnow().isoformat()
        
        return test_results
        
    except Exception as e:
        test_results["overall_status"] = "error"
        test_results["error"] = str(e)
        test_results["completed_at"] = datetime.utcnow().isoformat()
        return test_results


@router.get("/agent-status")
async def get_agent_status():
    """Get comprehensive status of all agents"""
    
    try:
        status = await agent_orchestrator.get_agent_status()
        
        # Add integration status
        integration_status = await agent_orchestrator.test_agent_integrations()
        
        return {
            "success": True,
            "agent_status": status,
            "integration_status": integration_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


@router.post("/test-agent/{agent_name}")
async def test_specific_agent(agent_name: str):
    """Test a specific agent"""
    
    try:
        if agent_name == "research_agent":
            result = await agent_orchestrator.research_agent.execute_task(
                "search_by_topics",
                {
                    "user_id": "test_user",
                    "topics": ["technology"],
                    "days_back": 1,
                    "max_results_per_topic": 2
                }
            )
        elif agent_name == "writing_agent":
            mock_articles = [{
                "title": "Test Article",
                "content": "Test content for writing agent",
                "url": "https://example.com",
                "topic": "technology"
            }]
            result = await agent_orchestrator.writing_agent.execute_task(
                "generate_newsletter",
                {
                    "user_id": "test_user",
                    "articles": mock_articles,
                    "user_preferences": {"tone": "professional"}
                }
            )
        elif agent_name == "preference_agent":
            result = await agent_orchestrator.preference_agent.execute_task(
                "get_preferences",
                {"user_id": "test_user"}
            )
        elif agent_name == "custom_prompt_agent":
            result = await agent_orchestrator.custom_prompt_agent.execute_task(
                "analyze_prompt",
                {
                    "custom_prompt": "Test prompt for analysis",
                    "user_preferences": {"tone": "professional"}
                }
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {agent_name}")
        
        return {
            "success": True,
            "agent": agent_name,
            "test_result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test {agent_name}: {str(e)}")


@router.post("/validate-integrations")
async def validate_external_integrations():
    """Validate external service integrations"""
    
    validations = {
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    try:
        # Test Tavily API (Research Agent dependency)
        try:
            from app.services.tavily import tavily_client
            if tavily_client and hasattr(tavily_client, 'search'):
                validations["services"]["tavily"] = {
                    "status": "configured",
                    "message": "Tavily API client is configured"
                }
            else:
                validations["services"]["tavily"] = {
                    "status": "not_configured", 
                    "message": "Tavily API client not properly configured"
                }
        except Exception as e:
            validations["services"]["tavily"] = {
                "status": "error",
                "message": f"Tavily API error: {str(e)}"
            }
        
        # Test Resend API (Email service dependency)
        try:
            from app.services.email import email_service
            if email_service and hasattr(email_service, 'api_key') and email_service.api_key:
                validations["services"]["resend"] = {
                    "status": "configured",
                    "message": "Resend API key is configured"
                }
            else:
                validations["services"]["resend"] = {
                    "status": "not_configured",
                    "message": "Resend API key not configured"
                }
        except Exception as e:
            validations["services"]["resend"] = {
                "status": "error",
                "message": f"Resend API error: {str(e)}"
            }
        
        # Test Upstash Redis (Memory service dependency)
        try:
            from app.services.upstash import get_redis_client
            redis_client = get_redis_client()
            if redis_client:
                validations["services"]["upstash_redis"] = {
                    "status": "configured",
                    "message": "Upstash Redis client is configured"
                }
            else:
                validations["services"]["upstash_redis"] = {
                    "status": "not_configured",
                    "message": "Upstash Redis not configured"
                }
        except Exception as e:
            validations["services"]["upstash_redis"] = {
                "status": "error",
                "message": f"Upstash Redis error: {str(e)}"
            }
        
        # Test Upstash Vector (RAG system dependency)
        try:
            from app.services.upstash import get_vector_client
            vector_client = get_vector_client()
            if vector_client:
                validations["services"]["upstash_vector"] = {
                    "status": "configured",
                    "message": "Upstash Vector client is configured"
                }
            else:
                validations["services"]["upstash_vector"] = {
                    "status": "not_configured",
                    "message": "Upstash Vector not configured"
                }
        except Exception as e:
            validations["services"]["upstash_vector"] = {
                "status": "error",
                "message": f"Upstash Vector error: {str(e)}"
            }
        
        # Test Portia AI
        try:
            from app.portia.config import get_portia_client
            portia_client = get_portia_client()
            if portia_client:
                validations["services"]["portia"] = {
                    "status": "configured",
                    "message": "Portia AI client is configured"
                }
            else:
                validations["services"]["portia"] = {
                    "status": "not_configured",
                    "message": "Portia AI client not configured"
                }
        except Exception as e:
            validations["services"]["portia"] = {
                "status": "error",
                "message": f"Portia AI error: {str(e)}"
            }
        
        # Calculate overall status
        service_statuses = [s["status"] for s in validations["services"].values()]
        configured_count = sum(1 for status in service_statuses if status == "configured")
        total_count = len(service_statuses)
        
        validations["summary"] = {
            "total_services": total_count,
            "configured_services": configured_count,
            "configuration_rate": (configured_count / total_count) * 100 if total_count > 0 else 0,
            "overall_status": "fully_configured" if configured_count == total_count else "partially_configured" if configured_count > 0 else "not_configured"
        }
        
        return validations
        
    except Exception as e:
        validations["error"] = str(e)
        validations["summary"] = {"overall_status": "error"}
        return validations