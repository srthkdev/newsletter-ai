"""
Newsletter Research Agent using Portia AI framework with Tavily integration
"""
from typing import Dict, Any, List, Optional
from portia import Plan, PlanBuilder
from app.portia.base_agent import BaseNewsletterAgent
from app.services.tavily import tavily_service
from app.services.memory import memory_service

class NewsletterResearchAgent(BaseNewsletterAgent):
    """Portia agent for discovering and curating newsletter content"""
    
    def __init__(self):
        super().__init__("research_agent")
        self.tavily = tavily_service
        self.memory = memory_service
    
    async def create_plan(self, context: Dict[str, Any]) -> Plan:
        """Create research plan using Portia PlanBuilder"""
        user_id = context.get("user_id")
        topics = context.get("topics", [])
        custom_prompt = context.get("custom_prompt")
        days_back = context.get("days_back", 3)
        
        builder = PlanBuilder()
        
        # Step 1: Analyze user preferences and context
        builder.add_step(
            "analyze_user_context",
            f"""
            Analyze the user's research context:
            - User ID: {user_id}
            - Topics of interest: {topics}
            - Custom prompt: {custom_prompt or 'None'}
            - Days to look back: {days_back}
            
            Based on this information, determine the best search strategy and keywords.
            Consider the user's preferences and any custom prompt to refine the search approach.
            """
        )
        
        # Step 2: Execute web search using Tavily
        builder.add_step(
            "execute_web_search",
            f"""
            Execute web search using the search strategy from the previous step.
            Search for recent, high-quality content related to the user's topics.
            Focus on finding articles from the last {days_back} days that are relevant and engaging.
            
            Use the Tavily search service to find content across multiple sources.
            """
        )
        
        # Step 3: Filter and score content quality
        builder.add_step(
            "filter_content_quality",
            """
            Filter the search results for quality and relevance:
            1. Remove duplicate or very similar articles
            2. Score articles based on content quality indicators
            3. Prioritize recent, well-written content from reputable sources
            4. Ensure content diversity across different subtopics
            
            Return the top 10-15 highest quality articles.
            """
        )
        
        # Step 4: Generate content summaries and insights
        builder.add_step(
            "generate_summaries",
            """
            For each selected article, generate:
            1. A concise summary (2-3 sentences)
            2. Key insights or takeaways
            3. Relevance score to user's interests
            4. Suggested newsletter section placement
            
            Focus on extracting the most valuable information for newsletter readers.
            """
        )
        
        # Step 5: Store research results in memory
        builder.add_step(
            "store_research_results",
            f"""
            Store the research results in the user's memory for future reference:
            - Save curated articles and summaries
            - Update user's reading patterns based on selected content
            - Store research metadata for analytics
            
            User ID: {user_id}
            """
        )
        
        return builder.build()
    
    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific research task"""
        if task == "search_by_topics":
            return await self._search_by_topics(context)
        elif task == "search_custom_prompt":
            return await self._search_custom_prompt(context)
        elif task == "get_trending_content":
            return await self._get_trending_content(context)
        else:
            return await self._execute_full_research(context)
    
    async def _search_by_topics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search for content based on user's selected topics"""
        topics = context.get("topics", [])
        days_back = context.get("days_back", 3)
        max_results_per_topic = context.get("max_results_per_topic", 5)
        
        if not topics:
            return {
                "success": False,
                "error": "No topics provided for search",
                "results": []
            }
        
        try:
            # Search using Tavily
            search_results = await self.tavily.search_by_topics(
                topics=topics,
                max_results_per_topic=max_results_per_topic,
                days_back=days_back
            )
            
            if not search_results["success"]:
                return search_results
            
            # Process and filter results
            all_articles = []
            for topic, topic_data in search_results["results_by_topic"].items():
                if topic_data["success"]:
                    for article in topic_data["results"]:
                        article["topic"] = topic
                        all_articles.append(article)
            
            # Filter for quality and remove duplicates
            filtered_articles = self.tavily.filter_content_by_quality(all_articles)
            unique_articles = self.tavily.detect_duplicates(filtered_articles)
            
            return {
                "success": True,
                "search_type": "topics",
                "topics": topics,
                "total_found": len(all_articles),
                "after_filtering": len(unique_articles),
                "articles": unique_articles[:15],  # Limit to top 15
                "search_metadata": search_results["search_metadata"]
            }
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    async def _search_custom_prompt(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search based on custom user prompt"""
        custom_prompt = context.get("custom_prompt", "")
        user_topics = context.get("topics", [])
        days_back = context.get("days_back", 3)
        
        if not custom_prompt:
            return {
                "success": False,
                "error": "No custom prompt provided",
                "results": []
            }
        
        try:
            # Extract search terms from custom prompt
            search_query = self._extract_search_terms(custom_prompt, user_topics)
            
            # Search using Tavily
            search_results = await self.tavily.search_news(
                query=search_query,
                days_back=days_back,
                max_results=20
            )
            
            if not search_results["success"]:
                return search_results
            
            # Filter and process results
            articles = search_results.get("results", [])
            filtered_articles = self.tavily.filter_content_by_quality(articles)
            unique_articles = self.tavily.detect_duplicates(filtered_articles)
            
            return {
                "success": True,
                "search_type": "custom_prompt",
                "original_prompt": custom_prompt,
                "search_query": search_query,
                "total_found": len(articles),
                "after_filtering": len(unique_articles),
                "articles": unique_articles[:15],
                "search_metadata": {
                    "days_back": days_back,
                    "custom_prompt": True
                }
            }
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    async def _get_trending_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get trending content across general topics"""
        trending_topics = [
            "artificial intelligence",
            "technology trends",
            "startup news",
            "business innovation",
            "science breakthroughs"
        ]
        
        context_with_trending = {
            **context,
            "topics": trending_topics,
            "days_back": 1,  # Very recent for trending
            "max_results_per_topic": 3
        }
        
        return await self._search_by_topics(context_with_trending)
    
    async def _execute_full_research(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full research workflow using Portia plan"""
        try:
            # Create and execute research plan
            plan = await self.create_plan(context)
            result = await self.run_plan(plan)
            
            if not result["success"]:
                return result
            
            # Process the research results to add summaries and insights
            articles = result.get("result", {}).get("articles", [])
            if articles:
                enhanced_articles = await self._generate_summaries_and_insights(articles)
                result["result"]["articles"] = enhanced_articles
            
            # Store results in memory for user
            user_id = context.get("user_id")
            if user_id and result.get("result"):
                await self.memory.store_user_context(
                    user_id=user_id,
                    context_type="research_results",
                    context_data={
                        "articles": result["result"].get("articles", []),
                        "search_metadata": result["result"].get("search_metadata", {}),
                        "research_timestamp": result["result"].get("timestamp"),
                        "content_analysis": await self.analyze_content_trends(articles)
                    },
                    ttl_hours=24
                )
            
            return result
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    def _extract_search_terms(self, custom_prompt: str, user_topics: List[str]) -> str:
        """Extract search terms from custom prompt and user topics"""
        # Simple keyword extraction - in production, could use NLP
        prompt_lower = custom_prompt.lower()
        
        # Look for specific keywords in the prompt
        search_terms = []
        
        # Add user topics as context
        if user_topics:
            search_terms.extend(user_topics[:2])  # Limit to top 2 topics
        
        # Extract key phrases from prompt
        key_phrases = [
            "artificial intelligence", "AI", "machine learning", "ML",
            "startup", "funding", "venture capital", "IPO",
            "technology", "tech", "innovation", "breakthrough",
            "business", "market", "industry", "company",
            "science", "research", "study", "discovery"
        ]
        
        for phrase in key_phrases:
            if phrase in prompt_lower:
                search_terms.append(phrase)
        
        # If no specific terms found, use the prompt directly
        if not search_terms:
            # Clean up the prompt for search
            search_terms = [custom_prompt.strip()[:100]]  # Limit length
        
        return " ".join(search_terms[:3])  # Combine top 3 terms
    
    async def get_user_research_history(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's recent research history from memory"""
        return await self.memory.get_user_context(user_id, "research_results")
    
    async def analyze_content_trends(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in the researched content"""
        if not articles:
            return {"trends": [], "topics": [], "sentiment": "neutral"}
        
        # Simple trend analysis
        topics_count = {}
        sources_count = {}
        
        for article in articles:
            # Count topics
            topic = article.get("topic", "general")
            topics_count[topic] = topics_count.get(topic, 0) + 1
            
            # Count sources
            url = article.get("url", "")
            if url:
                domain = url.split("//")[-1].split("/")[0]
                sources_count[domain] = sources_count.get(domain, 0) + 1
        
        # Sort by frequency
        top_topics = sorted(topics_count.items(), key=lambda x: x[1], reverse=True)
        top_sources = sorted(sources_count.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_articles": len(articles),
            "top_topics": top_topics[:5],
            "top_sources": top_sources[:5],
            "content_diversity": len(topics_count),
            "source_diversity": len(sources_count)
        }

# Global research agent instance
research_agent = NewsletterResearchAgent()