"""
Agent Orchestrator for coordinating all Newsletter AI agents
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.portia.research_agent import research_agent
from app.portia.writing_agent import writing_agent
from app.portia.preference_agent import preference_agent
from app.portia.custom_prompt_agent import custom_prompt_agent
from app.services.email import email_service
from app.services.memory import memory_service


class NewsletterAgentOrchestrator:
    """Orchestrates all newsletter AI agents for complete workflow execution"""

    def __init__(self):
        self.research_agent = research_agent
        self.writing_agent = writing_agent
        self.preference_agent = preference_agent
        self.custom_prompt_agent = custom_prompt_agent
        self.email_service = email_service
        self.memory_service = memory_service

    async def generate_newsletter(
        self,
        user_id: str,
        custom_prompt: Optional[str] = None,
        send_email: bool = False,
        user_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Complete newsletter generation workflow

        Args:
            user_id: User identifier
            custom_prompt: Optional custom prompt for newsletter generation
            send_email: Whether to send the newsletter via email
            user_email: User's email address (required if send_email=True)

        Returns:
            Dictionary containing the generated newsletter and workflow results
        """
        workflow_results = {
            "user_id": user_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "steps": {},
            "success": False,
            "newsletter": None,
            "email_sent": False,
        }

        try:
            # Step 1: Get user preferences
            print("🔄 Step 1: Getting user preferences...")
            preferences_result = await self.preference_agent.execute_task(
                "get_preferences", {"user_id": user_id}
            )

            workflow_results["steps"]["preferences"] = preferences_result

            if not preferences_result["success"]:
                workflow_results["error"] = "Failed to get user preferences"
                return workflow_results

            user_preferences = preferences_result["preferences"]

            # Step 2: Process custom prompt if provided
            research_context = {
                "user_id": user_id,
                "user_preferences": user_preferences,
                "topics": user_preferences.get("topics", []),
                "days_back": 3,
            }

            if custom_prompt:
                print("🔄 Step 2: Processing custom prompt...")
                prompt_result = await self.custom_prompt_agent.execute_task(
                    "process_prompt",
                    {
                        "user_id": user_id,
                        "custom_prompt": custom_prompt,
                        "user_preferences": user_preferences,
                    },
                )

                workflow_results["steps"]["custom_prompt"] = prompt_result

                if prompt_result["success"]:
                    # Update research context with custom prompt parameters
                    research_params = prompt_result.get("research_parameters", {})
                    research_context.update(
                        {
                            "custom_prompt": custom_prompt,
                            "topics": research_params.get(
                                "topics", research_context["topics"]
                            ),
                            "days_back": research_params.get("days_back", 3),
                            "max_results": research_params.get("max_results", 15),
                        }
                    )

            # Step 3: Research content
            print("🔄 Step 3: Researching content...")
            if custom_prompt:
                research_result = await self.research_agent.execute_task(
                    "search_custom_prompt", research_context
                )
            else:
                research_result = await self.research_agent.execute_task(
                    "search_by_topics", research_context
                )

            workflow_results["steps"]["research"] = research_result

            if not research_result["success"]:
                workflow_results["error"] = "Failed to research content"
                return workflow_results

            articles = research_result.get("articles", [])
            if not articles:
                workflow_results["error"] = (
                    "No articles found for newsletter generation"
                )
                return workflow_results

            # Step 4: Generate newsletter content
            print("🔄 Step 4: Generating newsletter content...")
            writing_context = {
                "user_id": user_id,
                "articles": articles,
                "user_preferences": user_preferences,
                "custom_prompt": custom_prompt,
            }

            # Add custom writing guidelines if available
            if custom_prompt and workflow_results["steps"].get("custom_prompt", {}).get(
                "success"
            ):
                writing_guidelines = workflow_results["steps"]["custom_prompt"].get(
                    "writing_guidelines", {}
                )
                writing_context["writing_guidelines"] = writing_guidelines

            writing_result = await self.writing_agent.execute_task(
                "generate_newsletter", writing_context
            )

            workflow_results["steps"]["writing"] = writing_result

            if not writing_result["success"]:
                workflow_results["error"] = "Failed to generate newsletter content"
                return workflow_results

            newsletter = writing_result["newsletter"]

            # Step 5: Format for email
            print("🔄 Step 5: Formatting newsletter for email...")
            format_result = await self.writing_agent.execute_task(
                "format_for_email", {"newsletter": newsletter}
            )

            workflow_results["steps"]["formatting"] = format_result

            if format_result["success"]:
                newsletter.update(
                    {
                        "html_content": format_result["html_content"],
                        "plain_text": format_result["plain_text"],
                    }
                )

            # Step 6: Generate subject lines
            print("🔄 Step 6: Generating subject lines...")
            subject_result = await self.writing_agent.execute_task(
                "create_subject_lines",
                {
                    "newsletter_content": newsletter,
                    "articles": articles,
                    "user_preferences": user_preferences,
                },
            )

            workflow_results["steps"]["subject_lines"] = subject_result

            if subject_result["success"]:
                newsletter["subject_lines"] = subject_result["subject_lines"]

            # Step 7: Send email if requested
            if send_email and user_email:
                print("🔄 Step 7: Sending newsletter email...")

                # Use the first subject line or create a default
                subject_lines = newsletter.get("subject_lines", [])
                subject_line = (
                    subject_lines[0]
                    if subject_lines
                    else f"📧 {newsletter.get('title', 'Your Newsletter')}"
                )

                email_sent = await self.email_service.send_newsletter_email(
                    email=user_email,
                    newsletter_data=newsletter,
                    subject_line=subject_line,
                )

                workflow_results["email_sent"] = email_sent
                workflow_results["steps"]["email"] = {
                    "success": email_sent,
                    "recipient": user_email,
                    "subject": subject_line,
                }

                if email_sent:
                    # Update engagement metrics
                    await self.memory_service.update_engagement_metrics(
                        user_id=user_id,
                        newsletter_id=newsletter.get("id", "generated_newsletter"),
                        action="sent",
                        metadata={"email": user_email, "subject": subject_line},
                    )

            # Step 8: Store newsletter in history
            print("🔄 Step 8: Storing newsletter in history...")
            newsletter_with_id = {
                **newsletter,
                "id": f"newsletter_{datetime.utcnow().isoformat()}",
                "generated_at": datetime.utcnow().isoformat(),
                "workflow_id": workflow_results.get("workflow_id"),
                "custom_prompt": custom_prompt,
                "articles_count": len(articles),
            }

            stored = await self.memory_service.store_newsletter_history(
                user_id=user_id, newsletter_data=newsletter_with_id
            )

            workflow_results["steps"]["storage"] = {
                "success": stored,
                "newsletter_id": newsletter_with_id["id"],
            }

            # Final results
            workflow_results.update(
                {
                    "success": True,
                    "newsletter": newsletter_with_id,
                    "completed_at": datetime.utcnow().isoformat(),
                    "total_articles": len(articles),
                    "word_count": writing_result.get("word_count", 0),
                    "estimated_read_time": writing_result.get("estimated_read_time", 0),
                }
            )

            print("✅ Newsletter generation workflow completed successfully!")
            return workflow_results

        except Exception as e:
            workflow_results.update(
                {
                    "success": False,
                    "error": f"Workflow error: {str(e)}",
                    "failed_at": datetime.utcnow().isoformat(),
                }
            )
            print(f"❌ Newsletter generation workflow failed: {e}")
            return workflow_results

    async def update_user_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user preferences using the preference agent"""
        return await self.preference_agent.execute_task(
            "update_preferences", {"user_id": user_id, "preferences": preferences}
        )

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences using the preference agent"""
        return await self.preference_agent.execute_task(
            "get_preferences", {"user_id": user_id}
        )

    async def analyze_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Analyze user preferences and behavior"""
        return await self.preference_agent.execute_task(
            "analyze_preferences", {"user_id": user_id}
        )

    async def get_preference_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get preference recommendations for user"""
        return await self.preference_agent.execute_task(
            "recommend_preferences", {"user_id": user_id}
        )

    async def research_content_only(
        self,
        user_id: str,
        topics: List[str],
        custom_prompt: Optional[str] = None,
        days_back: int = 3,
    ) -> Dict[str, Any]:
        """Research content without generating newsletter"""
        context = {"user_id": user_id, "topics": topics, "days_back": days_back}

        if custom_prompt:
            context["custom_prompt"] = custom_prompt
            return await self.research_agent.execute_task(
                "search_custom_prompt", context
            )
        else:
            return await self.research_agent.execute_task("search_by_topics", context)

    async def get_newsletter_history(
        self, user_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user's newsletter history"""
        return await self.memory_service.get_newsletter_history(user_id, limit)

    async def get_user_engagement_metrics(
        self, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get user engagement metrics"""
        return await self.memory_service.get_engagement_metrics(user_id)

    async def process_custom_prompt_only(
        self,
        user_id: str,
        custom_prompt: str,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process custom prompt without generating newsletter"""
        if not user_preferences:
            prefs_result = await self.get_user_preferences(user_id)
            user_preferences = (
                prefs_result.get("preferences", {}) if prefs_result["success"] else {}
            )

        return await self.custom_prompt_agent.execute_task(
            "process_prompt",
            {
                "user_id": user_id,
                "custom_prompt": custom_prompt,
                "user_preferences": user_preferences,
            },
        )

    async def get_prompt_examples(self) -> List[Dict[str, Any]]:
        """Get example prompts for user guidance"""
        return await self.custom_prompt_agent.get_prompt_examples()

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "research_agent": {
                "name": self.research_agent.name,
                "description": self.research_agent.description,
                "status": "active",
            },
            "writing_agent": {
                "name": self.writing_agent.name,
                "description": self.writing_agent.description,
                "status": "active",
            },
            "preference_agent": {
                "name": self.preference_agent.name,
                "description": self.preference_agent.description,
                "status": "active",
            },
            "custom_prompt_agent": {
                "name": self.custom_prompt_agent.name,
                "description": self.custom_prompt_agent.description,
                "status": "active",
            },
            "email_service": {
                "name": "Email Service",
                "description": "Resend API integration for email delivery",
                "status": "active" if self.email_service.api_key else "inactive",
            },
            "memory_service": {
                "name": "Memory Service",
                "description": "Upstash Redis for user context and preferences",
                "status": "active" if self.memory_service.redis_url else "inactive",
            },
        }

    async def test_agent_integrations(self) -> Dict[str, Any]:
        """Test all agent integrations"""
        test_results = {}

        # Test research agent with Tavily
        try:
            test_research = await self.research_agent.execute_task(
                "search_by_topics",
                {
                    "user_id": "test_user",
                    "topics": ["technology"],
                    "days_back": 1,
                    "max_results_per_topic": 2,
                },
            )
            test_results["research_agent"] = {
                "status": "success" if test_research["success"] else "error",
                "message": test_research.get("error", "Working correctly"),
            }
        except Exception as e:
            test_results["research_agent"] = {"status": "error", "message": str(e)}

        # Test preference agent with memory
        try:
            test_prefs = await self.preference_agent.execute_task(
                "get_preferences", {"user_id": "test_user"}
            )
            test_results["preference_agent"] = {
                "status": "success" if test_prefs["success"] else "error",
                "message": test_prefs.get("error", "Working correctly"),
            }
        except Exception as e:
            test_results["preference_agent"] = {"status": "error", "message": str(e)}

        # Test custom prompt agent
        try:
            test_prompt = await self.custom_prompt_agent.execute_task(
                "analyze_prompt",
                {
                    "custom_prompt": "Create a newsletter about AI",
                    "user_preferences": {"tone": "professional"},
                },
            )
            test_results["custom_prompt_agent"] = {
                "status": "success" if test_prompt["success"] else "error",
                "message": test_prompt.get("error", "Working correctly"),
            }
        except Exception as e:
            test_results["custom_prompt_agent"] = {"status": "error", "message": str(e)}

        # Test email service
        test_results["email_service"] = {
            "status": "active" if self.email_service.api_key else "inactive",
            "message": "Resend API key configured"
            if self.email_service.api_key
            else "Resend API key not configured",
        }

        # Test memory service
        test_results["memory_service"] = {
            "status": "active" if self.memory_service.redis_url else "inactive",
            "message": "Upstash Redis configured"
            if self.memory_service.redis_url
            else "Upstash Redis not configured",
        }

        return {
            "overall_status": "healthy"
            if all(
                result["status"] in ["success", "active"]
                for result in test_results.values()
            )
            else "degraded",
            "test_results": test_results,
            "tested_at": datetime.utcnow().isoformat(),
        }


# Global orchestrator instance
agent_orchestrator = NewsletterAgentOrchestrator()
