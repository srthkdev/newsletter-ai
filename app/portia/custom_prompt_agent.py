"""
Custom Prompt Agent using Portia AI framework for processing user-defined newsletter requests
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from portia import Plan, PlanBuilder
from app.portia.base_agent import BaseNewsletterAgent
from app.services.memory import memory_service

class CustomPromptAgent(BaseNewsletterAgent):
    """Portia agent for processing custom user prompts for newsletter generation"""
    
    def __init__(self):
        super().__init__("custom_prompt_agent")
        self.memory = memory_service
    
    async def create_plan(self, context: Dict[str, Any]) -> Plan:
        """Create custom prompt processing plan using Portia PlanBuilder"""
        user_id = context.get("user_id")
        custom_prompt = context.get("custom_prompt", "")
        user_preferences = context.get("user_preferences", {})
        
        builder = PlanBuilder()
        
        # Step 1: Analyze and parse the custom prompt
        builder.add_step(
            "analyze_custom_prompt",
            f"""
            Analyze the user's custom prompt for newsletter generation:
            
            Custom Prompt: "{custom_prompt}"
            User Preferences: {user_preferences}
            
            Extract and identify:
            1. Specific topics or themes requested
            2. Desired tone or style (if mentioned)
            3. Content type preferences (news, analysis, tutorials, etc.)
            4. Time frame or recency requirements
            5. Any specific sources or domains mentioned
            6. Special formatting or structure requests
            
            Determine how this prompt should modify the standard newsletter generation process.
            """
        )
        
        # Step 2: Retrieve relevant context from user's history
        builder.add_step(
            "retrieve_user_context",
            f"""
            Retrieve relevant context from the user's newsletter history and preferences:
            - Previous newsletters with similar themes
            - User's engagement patterns with related content
            - Personalization data that might enhance the prompt
            
            Use this context to better understand the user's intent and preferences.
            User ID: {user_id}
            """
        )
        
        # Step 3: Enhance and refine the prompt
        builder.add_step(
            "enhance_prompt",
            """
            Enhance the original prompt by:
            1. Adding context from user preferences where appropriate
            2. Clarifying ambiguous requests
            3. Suggesting additional relevant topics if the prompt is too narrow
            4. Ensuring the prompt will generate engaging, valuable content
            5. Maintaining the user's original intent while optimizing for quality
            
            Create an enhanced prompt that will guide the research and writing agents effectively.
            """
        )
        
        # Step 4: Generate research parameters
        builder.add_step(
            "generate_research_parameters",
            """
            Based on the analyzed and enhanced prompt, generate specific parameters for the research agent:
            1. Search keywords and topics
            2. Content sources and domains to prioritize
            3. Time frame for content discovery
            4. Content types to focus on
            5. Quality and relevance criteria
            
            These parameters will ensure the research agent finds content that matches the user's request.
            """
        )
        
        # Step 5: Generate writing guidelines
        builder.add_step(
            "generate_writing_guidelines",
            """
            Create specific writing guidelines for the writing agent based on the prompt:
            1. Tone and style requirements
            2. Content structure and organization
            3. Key themes to emphasize
            4. Audience considerations
            5. Special formatting or presentation requirements
            
            These guidelines will ensure the final newsletter matches the user's vision.
            """
        )
        
        # Step 6: Validate and finalize processing
        builder.add_step(
            "validate_processing",
            """
            Validate that the prompt processing is complete and accurate:
            1. Ensure all aspects of the original prompt are addressed
            2. Verify that research parameters and writing guidelines are consistent
            3. Check that the processing maintains user preferences where appropriate
            4. Confirm that the output will be actionable for other agents
            
            Provide a summary of how the prompt will be executed.
            """
        )
        
        return builder.build()
    
    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific custom prompt processing task"""
        if task == "process_prompt":
            return await self._process_prompt(context)
        elif task == "analyze_prompt":
            return await self._analyze_prompt(context)
        elif task == "enhance_prompt":
            return await self._enhance_prompt(context)
        elif task == "generate_parameters":
            return await self._generate_parameters(context)
        else:
            return await self._execute_full_prompt_processing(context)
    
    async def _process_prompt(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process custom prompt and generate parameters for other agents"""
        try:
            custom_prompt = context.get("custom_prompt", "")
            user_id = context.get("user_id")
            user_preferences = context.get("user_preferences", {})
            
            if not custom_prompt.strip():
                return {
                    "success": False,
                    "error": "No custom prompt provided"
                }
            
            # Analyze the prompt
            analysis = await self._analyze_prompt_content(custom_prompt, user_preferences)
            
            # Get user context from memory
            user_context = await self._get_user_context(user_id)
            
            # Enhance the prompt with context
            enhanced_prompt = await self._enhance_prompt_with_context(
                custom_prompt, analysis, user_context, user_preferences
            )
            
            # Generate research parameters
            research_params = await self._generate_research_parameters(enhanced_prompt, analysis)
            
            # Generate writing guidelines
            writing_guidelines = await self._generate_writing_guidelines(enhanced_prompt, analysis)
            
            # Store the processed prompt for future reference
            if user_id:
                await self._store_prompt_processing(user_id, {
                    "original_prompt": custom_prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "analysis": analysis,
                    "research_params": research_params,
                    "writing_guidelines": writing_guidelines
                })
            
            return {
                "success": True,
                "original_prompt": custom_prompt,
                "enhanced_prompt": enhanced_prompt,
                "analysis": analysis,
                "research_parameters": research_params,
                "writing_guidelines": writing_guidelines,
                "processing_metadata": {
                    "processed_at": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "has_user_context": bool(user_context)
                }
            }
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    async def _analyze_prompt(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze custom prompt to extract key information"""
        try:
            custom_prompt = context.get("custom_prompt", "")
            user_preferences = context.get("user_preferences", {})
            
            analysis = await self._analyze_prompt_content(custom_prompt, user_preferences)
            
            return {
                "success": True,
                "analysis": analysis,
                "original_prompt": custom_prompt
            }
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    async def _enhance_prompt(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance custom prompt with user context and preferences"""
        try:
            custom_prompt = context.get("custom_prompt", "")
            user_id = context.get("user_id")
            user_preferences = context.get("user_preferences", {})
            
            # Get analysis
            analysis = await self._analyze_prompt_content(custom_prompt, user_preferences)
            
            # Get user context
            user_context = await self._get_user_context(user_id)
            
            # Enhance the prompt
            enhanced_prompt = await self._enhance_prompt_with_context(
                custom_prompt, analysis, user_context, user_preferences
            )
            
            return {
                "success": True,
                "original_prompt": custom_prompt,
                "enhanced_prompt": enhanced_prompt,
                "enhancements_applied": self._get_enhancements_applied(custom_prompt, enhanced_prompt)
            }
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    async def _generate_parameters(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate research and writing parameters from processed prompt"""
        try:
            enhanced_prompt = context.get("enhanced_prompt", "")
            analysis = context.get("analysis", {})
            
            if not enhanced_prompt:
                # If no enhanced prompt, process the original
                process_result = await self._process_prompt(context)
                if not process_result["success"]:
                    return process_result
                
                enhanced_prompt = process_result["enhanced_prompt"]
                analysis = process_result["analysis"]
            
            # Generate parameters
            research_params = await self._generate_research_parameters(enhanced_prompt, analysis)
            writing_guidelines = await self._generate_writing_guidelines(enhanced_prompt, analysis)
            
            return {
                "success": True,
                "research_parameters": research_params,
                "writing_guidelines": writing_guidelines,
                "enhanced_prompt": enhanced_prompt
            }
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    async def _execute_full_prompt_processing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full prompt processing workflow using Portia plan"""
        try:
            # Create and execute prompt processing plan
            plan = await self.create_plan(context)
            result = await self.run_plan(plan)
            
            return result
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    async def _analyze_prompt_content(
        self, 
        custom_prompt: str, 
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze the content of a custom prompt"""
        
        prompt_lower = custom_prompt.lower()
        
        # Extract topics mentioned
        topic_keywords = {
            "technology": ["tech", "technology", "software", "hardware", "digital"],
            "artificial intelligence": ["ai", "artificial intelligence", "machine learning", "ml", "neural", "deep learning"],
            "business": ["business", "company", "corporate", "enterprise", "market"],
            "startups": ["startup", "startups", "entrepreneur", "venture", "funding"],
            "science": ["science", "research", "study", "discovery", "breakthrough"],
            "finance": ["finance", "financial", "money", "investment", "crypto", "blockchain"],
            "health": ["health", "medical", "healthcare", "medicine", "wellness"],
            "cybersecurity": ["security", "cyber", "hacking", "privacy", "data protection"]
        }
        
        detected_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_topics.append(topic)
        
        # Extract tone indicators
        tone_indicators = {
            "casual": ["casual", "friendly", "conversational", "relaxed", "informal"],
            "professional": ["professional", "formal", "business", "corporate"],
            "technical": ["technical", "detailed", "in-depth", "analytical", "expert"]
        }
        
        detected_tone = user_preferences.get("tone", "professional")  # Default to user preference
        for tone, indicators in tone_indicators.items():
            if any(indicator in prompt_lower for indicator in indicators):
                detected_tone = tone
                break
        
        # Extract time frame indicators
        time_indicators = {
            "today": ["today", "today's"],
            "this_week": ["this week", "weekly", "week"],
            "recent": ["recent", "latest", "new", "current"],
            "trending": ["trending", "popular", "viral", "hot"]
        }
        
        time_frame = "recent"  # Default
        for frame, indicators in time_indicators.items():
            if any(indicator in prompt_lower for indicator in indicators):
                time_frame = frame
                break
        
        # Extract content type preferences
        content_types = {
            "news": ["news", "updates", "headlines", "breaking"],
            "analysis": ["analysis", "insights", "deep dive", "breakdown"],
            "tutorials": ["tutorial", "how-to", "guide", "tips"],
            "reviews": ["review", "comparison", "evaluation"]
        }
        
        detected_content_types = []
        for content_type, keywords in content_types.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_content_types.append(content_type)
        
        if not detected_content_types:
            detected_content_types = ["news"]  # Default to news
        
        # Calculate specificity score
        specificity_score = len(detected_topics) + len(detected_content_types)
        if len(custom_prompt.split()) > 10:
            specificity_score += 1
        
        return {
            "detected_topics": detected_topics,
            "detected_tone": detected_tone,
            "time_frame": time_frame,
            "content_types": detected_content_types,
            "specificity_score": specificity_score,
            "prompt_length": len(custom_prompt),
            "word_count": len(custom_prompt.split()),
            "has_specific_request": specificity_score > 2,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context from memory"""
        if not user_id:
            return {}
        
        # Get user preferences
        preferences = await self.memory.get_user_preferences(user_id)
        
        # Get recent newsletter history
        recent_newsletters = await self.memory.get_newsletter_history(user_id, limit=3)
        
        # Get reading patterns
        reading_patterns = await self.memory.get_reading_patterns(user_id)
        
        return {
            "preferences": preferences or {},
            "recent_newsletters": recent_newsletters,
            "reading_patterns": reading_patterns or {},
            "has_history": bool(recent_newsletters)
        }
    
    async def _enhance_prompt_with_context(
        self,
        original_prompt: str,
        analysis: Dict[str, Any],
        user_context: Dict[str, Any],
        user_preferences: Dict[str, Any]
    ) -> str:
        """Enhance the original prompt with user context and preferences"""
        
        enhanced_parts = [original_prompt]
        
        # Add user topic preferences if not mentioned in prompt
        user_topics = user_preferences.get("topics", [])
        detected_topics = analysis.get("detected_topics", [])
        
        missing_topics = [topic for topic in user_topics if topic not in detected_topics]
        if missing_topics and len(detected_topics) < 3:
            enhanced_parts.append(f"Also include content related to: {', '.join(missing_topics[:2])}")
        
        # Add tone preference if not specified
        if analysis.get("detected_tone") == user_preferences.get("tone", "professional"):
            # Tone matches, no need to add
            pass
        else:
            # Add user's preferred tone
            preferred_tone = user_preferences.get("tone", "professional")
            enhanced_parts.append(f"Use a {preferred_tone} tone throughout the newsletter.")
        
        # Add context from reading patterns
        reading_patterns = user_context.get("reading_patterns", {})
        if reading_patterns.get("preferred_topics"):
            preferred = reading_patterns["preferred_topics"][:2]
            if not any(topic in detected_topics for topic in preferred):
                enhanced_parts.append(f"Consider including content about {', '.join(preferred)} based on reading history.")
        
        # Add recency preference if not specified
        if analysis.get("time_frame") == "recent":
            frequency = user_preferences.get("frequency", "weekly")
            if frequency == "daily":
                enhanced_parts.append("Focus on content from the last 24 hours.")
            elif frequency == "weekly":
                enhanced_parts.append("Include content from the past week.")
        
        return " ".join(enhanced_parts)
    
    async def _generate_research_parameters(
        self, 
        enhanced_prompt: str, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate research parameters for the research agent"""
        
        detected_topics = analysis.get("detected_topics", [])
        time_frame = analysis.get("time_frame", "recent")
        content_types = analysis.get("content_types", ["news"])
        
        # Map time frame to days back
        days_back_mapping = {
            "today": 1,
            "this_week": 7,
            "recent": 3,
            "trending": 1
        }
        
        days_back = days_back_mapping.get(time_frame, 3)
        
        # Determine search strategy
        if detected_topics:
            search_strategy = "topic_focused"
            search_topics = detected_topics
        else:
            search_strategy = "custom_query"
            search_topics = []
        
        # Set result limits based on specificity
        specificity_score = analysis.get("specificity_score", 1)
        max_results = min(20, max(10, specificity_score * 3))
        
        return {
            "search_strategy": search_strategy,
            "topics": search_topics,
            "custom_query": enhanced_prompt if search_strategy == "custom_query" else None,
            "days_back": days_back,
            "max_results": max_results,
            "content_types": content_types,
            "include_trending": "trending" in time_frame,
            "quality_threshold": "high" if specificity_score > 3 else "medium"
        }
    
    async def _generate_writing_guidelines(
        self, 
        enhanced_prompt: str, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate writing guidelines for the writing agent"""
        
        detected_tone = analysis.get("detected_tone", "professional")
        content_types = analysis.get("content_types", ["news"])
        detected_topics = analysis.get("detected_topics", [])
        
        # Determine structure based on content types
        if "analysis" in content_types:
            structure_style = "analytical"
        elif "tutorial" in content_types:
            structure_style = "instructional"
        else:
            structure_style = "informational"
        
        # Set personalization level
        specificity_score = analysis.get("specificity_score", 1)
        personalization_level = "high" if specificity_score > 3 else "medium"
        
        return {
            "tone": detected_tone,
            "structure_style": structure_style,
            "personalization_level": personalization_level,
            "focus_topics": detected_topics,
            "content_emphasis": content_types,
            "custom_requirements": {
                "original_prompt": enhanced_prompt,
                "maintain_user_intent": True,
                "highlight_requested_themes": True
            },
            "formatting": {
                "include_sections": len(detected_topics) > 2,
                "add_takeaways": "analysis" in content_types,
                "include_links": True
            }
        }
    
    async def _store_prompt_processing(
        self, 
        user_id: str, 
        processing_data: Dict[str, Any]
    ) -> bool:
        """Store prompt processing results in memory"""
        try:
            return await self.memory.store_user_context(
                user_id=user_id,
                context_type="custom_prompt_processing",
                context_data=processing_data,
                ttl_hours=24
            )
        except Exception as e:
            print(f"❌ Failed to store prompt processing: {e}")
            return False
    
    def _get_enhancements_applied(self, original: str, enhanced: str) -> List[str]:
        """Get list of enhancements applied to the prompt"""
        enhancements = []
        
        if len(enhanced) > len(original):
            enhancements.append("Added context from user preferences")
        
        if "tone" in enhanced.lower() and "tone" not in original.lower():
            enhancements.append("Added tone specification")
        
        if "include" in enhanced.lower() and "include" not in original.lower():
            enhancements.append("Added topic suggestions")
        
        if "focus on" in enhanced.lower() and "focus" not in original.lower():
            enhancements.append("Added time frame specification")
        
        if not enhancements:
            enhancements.append("Prompt was already comprehensive")
        
        return enhancements
    
    async def get_prompt_examples(self) -> List[Dict[str, Any]]:
        """Get example prompts for user guidance"""
        return [
            {
                "category": "Technology",
                "prompt": "Create a newsletter about AI breakthroughs this week with a technical tone",
                "description": "Focus on recent AI developments with detailed analysis"
            },
            {
                "category": "Business",
                "prompt": "Focus on startup funding news with a casual, conversational style",
                "description": "Cover venture capital and startup news in an approachable way"
            },
            {
                "category": "Science",
                "prompt": "Summarize the latest developments in renewable energy for business professionals",
                "description": "Professional overview of clean energy advances"
            },
            {
                "category": "General",
                "prompt": "Generate a newsletter about space exploration with an enthusiastic tone",
                "description": "Exciting updates from space industry and research"
            },
            {
                "category": "Security",
                "prompt": "Cover cybersecurity trends with practical tips for developers",
                "description": "Security news with actionable developer insights"
            },
            {
                "category": "Finance",
                "prompt": "Create content about fintech innovations with a professional tone",
                "description": "Financial technology updates for business audience"
            }
        ]

# Global custom prompt agent instance
custom_prompt_agent = CustomPromptAgent()