"""
Newsletter Preference Agent using Portia AI framework for managing user settings
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from portia import Plan, PlanBuilder
from app.portia.base_agent import BaseNewsletterAgent
from app.services.memory import memory_service


class NewsletterPreferenceAgent(BaseNewsletterAgent):
    """Portia agent for managing user preferences and personalization"""

    def __init__(self):
        super().__init__("preference_agent")
        self.memory = memory_service

    async def create_plan(self, context: Dict[str, Any]) -> Plan:
        """Create preference management plan using Portia PlanBuilder"""
        user_id = context.get("user_id")
        action = context.get("action", "update")  # update, analyze, recommend
        preferences = context.get("preferences", {})

        builder = PlanBuilder()

        if action == "update":
            # Plan for updating user preferences
            builder.add_step(
                "validate_preferences",
                f"""
                Validate the provided user preferences:
                - Topics: {preferences.get("topics", [])}
                - Tone: {preferences.get("tone", "professional")}
                - Frequency: {preferences.get("frequency", "weekly")}
                - Custom settings: {preferences.get("custom_settings", {})}
                
                Ensure all preferences are valid and consistent.
                Check for any conflicts or missing required settings.
                """,
            )

            builder.add_step(
                "store_preferences",
                f"""
                Store the validated preferences in the user's memory:
                - User ID: {user_id}
                - Update timestamp and version tracking
                - Maintain preference history for analytics
                
                Ensure the preferences are properly saved and accessible.
                """,
            )

            builder.add_step(
                "generate_personalization_profile",
                """
                Generate a personalization profile based on the new preferences:
                1. Create content filtering rules
                2. Set up search parameters for research agent
                3. Configure writing style guidelines
                4. Establish frequency and timing preferences
                
                This profile will be used by other agents for personalization.
                """,
            )

        elif action == "analyze":
            # Plan for analyzing user preferences and behavior
            builder.add_step(
                "analyze_current_preferences",
                f"""
                Analyze the user's current preferences and usage patterns:
                - Current preference settings
                - Newsletter engagement history
                - Reading patterns and behavior
                - Content interaction data
                
                User ID: {user_id}
                """,
            )

            builder.add_step(
                "identify_optimization_opportunities",
                """
                Identify opportunities to optimize the user's newsletter experience:
                1. Topics that might interest them based on behavior
                2. Optimal frequency based on engagement
                3. Tone adjustments based on interaction patterns
                4. Content format preferences
                
                Provide actionable recommendations.
                """,
            )

        elif action == "recommend":
            # Plan for generating preference recommendations
            builder.add_step(
                "analyze_user_behavior",
                f"""
                Analyze user behavior to generate preference recommendations:
                - Newsletter open rates and click patterns
                - Time spent reading different content types
                - Topics that generate most engagement
                - Preferred content length and format
                
                User ID: {user_id}
                """,
            )

            builder.add_step(
                "generate_recommendations",
                """
                Generate personalized preference recommendations:
                1. Suggest new topics based on interests
                2. Recommend optimal frequency and timing
                3. Suggest tone adjustments for better engagement
                4. Propose content format improvements
                
                Provide clear rationale for each recommendation.
                """,
            )

        return builder.build()

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific preference management task"""
        if task == "update_preferences":
            return await self._update_preferences(context)
        elif task == "get_preferences":
            return await self._get_preferences(context)
        elif task == "analyze_preferences":
            return await self._analyze_preferences(context)
        elif task == "recommend_preferences":
            return await self._recommend_preferences(context)
        else:
            return await self._execute_full_preference_management(context)

    async def _update_preferences(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        try:
            user_id = context.get("user_id")
            preferences = context.get("preferences", {})

            if not user_id:
                return {
                    "success": False,
                    "error": "User ID is required for preference updates",
                }

            # Validate preferences
            validated_preferences = self._validate_preferences(preferences)
            if not validated_preferences["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid preferences: {validated_preferences['errors']}",
                }

            # Add metadata
            preferences_with_metadata = {
                **preferences,
                "updated_at": datetime.utcnow().isoformat(),
                "version": "1.0",
                "validation_passed": True,
            }

            # Store in memory
            success = await self.memory.store_user_preferences(
                user_id, preferences_with_metadata
            )

            if success:
                # Generate personalization profile
                profile = await self._generate_personalization_profile(
                    preferences_with_metadata
                )

                return {
                    "success": True,
                    "preferences": preferences_with_metadata,
                    "personalization_profile": profile,
                    "message": "Preferences updated successfully",
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to store preferences in memory",
                }

        except Exception as e:
            return await self.handle_error(e, context)

    async def _get_preferences(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            user_id = context.get("user_id")

            if not user_id:
                return {"success": False, "error": "User ID is required"}

            # Try memory service first
            preferences = await self.memory.get_user_preferences(user_id)
            
            # If memory service fails or returns empty, try database directly
            if not preferences:
                try:
                    from app.core.database import get_db
                    from app.models.preferences import UserPreferences
                    from sqlalchemy.orm import Session
                    import uuid
                    
                    # Get database session
                    db_gen = get_db()
                    db: Session = next(db_gen)
                    
                    try:
                        # Convert user_id to UUID if needed
                        if isinstance(user_id, str):
                            if user_id == "demo_user":
                                # For demo user, create a consistent UUID
                                user_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
                            else:
                                try:
                                    user_uuid = uuid.UUID(user_id)
                                except ValueError:
                                    # If user_id is not a valid UUID, create one from the string
                                    import hashlib
                                    user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:32]
                                    user_uuid = uuid.UUID(user_hash[:8] + '-' + user_hash[8:12] + '-' + user_hash[12:16] + '-' + user_hash[16:20] + '-' + user_hash[20:32])
                        else:
                            user_uuid = user_id
                        
                        # Query database directly
                        db_preferences = db.query(UserPreferences).filter(
                            UserPreferences.user_id == user_uuid
                        ).first()
                        
                        if db_preferences:
                            preferences = {
                                "topics": db_preferences.topics or ["technology", "business"],
                                "tone": db_preferences.tone or "professional",
                                "frequency": db_preferences.frequency or "weekly",
                                "max_articles": db_preferences.max_articles_per_newsletter or 10,
                                "include_trending": getattr(db_preferences, 'include_trending', True),
                                "custom_instructions": db_preferences.custom_instructions or "",
                                "preferred_length": db_preferences.preferred_length or "medium",
                                "timezone": db_preferences.timezone or "UTC",
                                "send_time": db_preferences.preferred_send_time.strftime("%H:%M") if db_preferences.preferred_send_time else "09:00",
                                "updated_at": db_preferences.updated_at.isoformat() if db_preferences.updated_at else None,
                                "loaded_from": "database_direct"
                            }
                            print(f"\u2139\ufe0f Loaded preferences directly from database for user {user_id}: {len(preferences.get('topics', []))} topics")
                        
                    finally:
                        db.close()
                        
                except Exception as db_error:
                    print(f"Database fallback failed: {db_error}")

            if preferences:
                return {
                    "success": True,
                    "preferences": preferences,
                    "has_preferences": True,
                }
            else:
                # Return default preferences
                default_preferences = self._get_default_preferences()
                print(f"\u26a0\ufe0f Using default preferences for user {user_id}")
                return {
                    "success": True,
                    "preferences": default_preferences,
                    "has_preferences": False,
                    "message": "Using default preferences",
                }

        except Exception as e:
            print(f"Error getting preferences: {e}")
            return await self.handle_error(e, context)

    async def _analyze_preferences(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user preferences and behavior"""
        try:
            user_id = context.get("user_id")

            if not user_id:
                return {"success": False, "error": "User ID is required for analysis"}

            # Get current preferences
            preferences = await self.memory.get_user_preferences(user_id)

            # Get engagement metrics
            engagement = await self.memory.get_engagement_metrics(user_id)

            # Get reading patterns
            reading_patterns = await self.memory.get_reading_patterns(user_id)

            # Analyze the data
            analysis = self._analyze_user_data(
                preferences, engagement, reading_patterns
            )

            return {
                "success": True,
                "analysis": analysis,
                "preferences": preferences,
                "engagement_summary": self._summarize_engagement(engagement),
                "reading_summary": self._summarize_reading_patterns(reading_patterns),
            }

        except Exception as e:
            return await self.handle_error(e, context)

    async def _recommend_preferences(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate preference recommendations"""
        try:
            user_id = context.get("user_id")

            # First analyze current state
            analysis_result = await self._analyze_preferences({"user_id": user_id})

            if not analysis_result["success"]:
                return analysis_result

            analysis = analysis_result["analysis"]
            current_preferences = analysis_result["preferences"]

            # Generate recommendations
            recommendations = self._generate_preference_recommendations(
                analysis, current_preferences
            )

            return {
                "success": True,
                "recommendations": recommendations,
                "current_preferences": current_preferences,
                "analysis_summary": analysis.get("summary", {}),
            }

        except Exception as e:
            return await self.handle_error(e, context)

    async def _execute_full_preference_management(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute full preference management workflow using Portia plan"""
        try:
            # Create and execute preference management plan
            plan = await self.create_plan(context)
            result = await self.run_plan(plan)

            return result

        except Exception as e:
            return await self.handle_error(e, context)

    def _validate_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user preferences"""
        errors = []

        # Validate topics
        topics = preferences.get("topics", [])
        if not isinstance(topics, list):
            errors.append("Topics must be a list")
        elif len(topics) == 0:
            errors.append("At least one topic must be selected")
        else:
            valid_topics = [
                "technology",
                "artificial intelligence",
                "business",
                "startups",
                "science",
                "health",
                "finance",
                "marketing",
                "productivity",
                "innovation",
                "cybersecurity",
                "data science",
                "software development",
            ]
            invalid_topics = [t for t in topics if t not in valid_topics]
            if invalid_topics:
                errors.append(f"Invalid topics: {invalid_topics}")

        # Validate tone
        tone = preferences.get("tone", "professional")
        valid_tones = ["professional", "casual", "technical"]
        if tone not in valid_tones:
            errors.append(f"Tone must be one of: {valid_tones}")

        # Validate frequency
        frequency = preferences.get("frequency", "weekly")
        valid_frequencies = ["daily", "every_2_days", "weekly", "monthly"]
        if frequency not in valid_frequencies:
            errors.append(f"Frequency must be one of: {valid_frequencies}")

        return {"valid": len(errors) == 0, "errors": errors}

    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            "topics": ["technology", "business"],
            "tone": "professional",
            "frequency": "weekly",
            "max_articles": 10,
            "include_trending": True,
            "custom_settings": {},
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0",
            "is_default": True,
        }

    async def _generate_personalization_profile(
        self, preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalization profile from preferences"""
        topics = preferences.get("topics", [])
        tone = preferences.get("tone", "professional")
        frequency = preferences.get("frequency", "weekly")

        # Create search parameters for research agent
        search_params = {
            "topics": topics,
            "max_results_per_topic": 5,
            "days_back": self._get_days_back_from_frequency(frequency),
            "include_trending": preferences.get("include_trending", True),
        }

        # Create writing guidelines for writing agent
        writing_guidelines = {
            "tone": tone,
            "max_articles": preferences.get("max_articles", 10),
            "preferred_sections": self._get_preferred_sections(topics),
            "personalization_level": "high" if len(topics) > 3 else "medium",
        }

        # Create delivery settings
        delivery_settings = {
            "frequency": frequency,
            "optimal_send_time": self._get_optimal_send_time(frequency),
            "format_preference": "html",  # Default to HTML
        }

        return {
            "search_params": search_params,
            "writing_guidelines": writing_guidelines,
            "delivery_settings": delivery_settings,
            "created_at": datetime.utcnow().isoformat(),
        }

    def _get_days_back_from_frequency(self, frequency: str) -> int:
        """Get number of days to look back based on frequency"""
        frequency_mapping = {"daily": 1, "every_2_days": 2, "weekly": 7, "monthly": 30}
        return frequency_mapping.get(frequency, 7)

    def _get_preferred_sections(self, topics: List[str]) -> List[str]:
        """Get preferred newsletter sections based on topics"""
        section_mapping = {
            "technology": ["Tech News", "Innovation"],
            "artificial intelligence": ["AI Updates", "Machine Learning"],
            "business": ["Business News", "Market Updates"],
            "startups": ["Startup News", "Funding Updates"],
            "science": ["Science Breakthroughs", "Research"],
            "finance": ["Financial News", "Market Analysis"],
        }

        sections = []
        for topic in topics:
            if topic in section_mapping:
                sections.extend(section_mapping[topic])

        return list(set(sections))  # Remove duplicates

    def _get_optimal_send_time(self, frequency: str) -> str:
        """Get optimal send time based on frequency"""
        if frequency == "daily":
            return "08:00"  # 8 AM
        elif frequency == "weekly":
            return "Monday 09:00"  # Monday 9 AM
        elif frequency == "monthly":
            return "First Monday 09:00"  # First Monday of month
        else:
            return "09:00"  # Default 9 AM

    def _analyze_user_data(
        self,
        preferences: Optional[Dict[str, Any]],
        engagement: Optional[Dict[str, Any]],
        reading_patterns: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze user data to provide insights"""

        analysis = {"summary": {}, "insights": [], "optimization_opportunities": []}

        # Analyze preferences
        if preferences:
            topics = preferences.get("topics", [])
            tone = preferences.get("tone", "professional")
            frequency = preferences.get("frequency", "weekly")

            analysis["summary"]["preferences"] = {
                "topic_count": len(topics),
                "primary_topics": topics[:3],
                "tone": tone,
                "frequency": frequency,
            }

            if len(topics) > 5:
                analysis["insights"].append(
                    "User has diverse interests with many topics selected"
                )
            elif len(topics) < 2:
                analysis["optimization_opportunities"].append(
                    "Consider adding more topics for better content variety"
                )

        # Analyze engagement
        if engagement:
            total_opens = engagement.get("total_opens", 0)
            total_clicks = engagement.get("total_clicks", 0)
            total_newsletters = engagement.get("total_newsletters", 1)

            open_rate = (
                (total_opens / total_newsletters) * 100 if total_newsletters > 0 else 0
            )
            click_rate = (total_clicks / total_opens) * 100 if total_opens > 0 else 0

            analysis["summary"]["engagement"] = {
                "open_rate": round(open_rate, 1),
                "click_rate": round(click_rate, 1),
                "total_newsletters": total_newsletters,
            }

            if open_rate < 30:
                analysis["optimization_opportunities"].append(
                    "Low open rate - consider improving subject lines or send timing"
                )
            if click_rate < 10:
                analysis["optimization_opportunities"].append(
                    "Low click rate - content might need to be more engaging"
                )

        # Analyze reading patterns
        if reading_patterns:
            analysis["summary"]["reading_patterns"] = reading_patterns

            # Add insights based on reading patterns
            if "preferred_topics" in reading_patterns:
                analysis["insights"].append(
                    f"Most engaged with: {reading_patterns['preferred_topics'][:3]}"
                )

        return analysis

    def _summarize_engagement(
        self, engagement: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize engagement metrics"""
        if not engagement:
            return {"status": "no_data"}

        total_opens = engagement.get("total_opens", 0)
        total_clicks = engagement.get("total_clicks", 0)
        total_newsletters = engagement.get("total_newsletters", 1)

        return {
            "total_newsletters": total_newsletters,
            "total_opens": total_opens,
            "total_clicks": total_clicks,
            "open_rate": round((total_opens / total_newsletters) * 100, 1)
            if total_newsletters > 0
            else 0,
            "click_rate": round((total_clicks / total_opens) * 100, 1)
            if total_opens > 0
            else 0,
            "engagement_level": self._calculate_engagement_level(
                total_opens, total_clicks, total_newsletters
            ),
        }

    def _summarize_reading_patterns(
        self, reading_patterns: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize reading patterns"""
        if not reading_patterns:
            return {"status": "no_data"}

        return {
            "has_patterns": True,
            "preferred_topics": reading_patterns.get("preferred_topics", []),
            "reading_frequency": reading_patterns.get("reading_frequency", "unknown"),
            "engagement_trends": reading_patterns.get("engagement_trends", {}),
        }

    def _calculate_engagement_level(
        self, opens: int, clicks: int, newsletters: int
    ) -> str:
        """Calculate overall engagement level"""
        if newsletters == 0:
            return "no_data"

        open_rate = (opens / newsletters) * 100
        click_rate = (clicks / opens) * 100 if opens > 0 else 0

        if open_rate >= 50 and click_rate >= 15:
            return "high"
        elif open_rate >= 30 and click_rate >= 8:
            return "medium"
        else:
            return "low"

    def _generate_preference_recommendations(
        self, analysis: Dict[str, Any], current_preferences: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate preference recommendations based on analysis"""
        recommendations = []

        if not current_preferences:
            recommendations.append(
                {
                    "type": "setup",
                    "title": "Complete Your Preferences",
                    "description": "Set up your newsletter preferences to get personalized content",
                    "action": "configure_preferences",
                    "priority": "high",
                }
            )
            return recommendations

        # Analyze optimization opportunities
        opportunities = analysis.get("optimization_opportunities", [])

        for opportunity in opportunities:
            if "topics" in opportunity.lower():
                recommendations.append(
                    {
                        "type": "topics",
                        "title": "Expand Your Topics",
                        "description": opportunity,
                        "action": "add_topics",
                        "priority": "medium",
                        "suggested_topics": [
                            "artificial intelligence",
                            "innovation",
                            "productivity",
                        ],
                    }
                )

            elif "open rate" in opportunity.lower():
                recommendations.append(
                    {
                        "type": "timing",
                        "title": "Optimize Send Timing",
                        "description": opportunity,
                        "action": "adjust_timing",
                        "priority": "high",
                        "suggested_changes": [
                            "Try different send times",
                            "Consider frequency adjustment",
                        ],
                    }
                )

            elif "click rate" in opportunity.lower():
                recommendations.append(
                    {
                        "type": "content",
                        "title": "Improve Content Engagement",
                        "description": opportunity,
                        "action": "adjust_tone",
                        "priority": "medium",
                        "suggested_changes": [
                            "Try a more casual tone",
                            "Include more actionable insights",
                        ],
                    }
                )

        # Add general recommendations if no specific opportunities found
        if not recommendations:
            recommendations.append(
                {
                    "type": "general",
                    "title": "Your Preferences Look Good",
                    "description": "Your current settings are working well. Consider trying new topics occasionally.",
                    "action": "maintain",
                    "priority": "low",
                }
            )

        return recommendations


# Global preference agent instance
preference_agent = NewsletterPreferenceAgent()
