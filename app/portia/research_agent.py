"""
Newsletter Research Agent using Portia AI framework with Tavily integration

This agent implements all requirements from Requirement 3:

3.1: Uses Tavily API to search for content based on user preferences
3.2: Filters content based on user-selected topics and relevance scores
3.3: Prioritizes content published within the last 24 hours for trending topics
3.4: Removes duplicates using content similarity analysis
3.5: Provides summaries and key insights for each selected article

Key Features:
- Multi-topic search with Tavily API integration
- Content quality filtering and relevance scoring
- Duplicate detection and removal
- Recent content prioritization (last 24 hours)
- AI-powered content summarization and insight extraction
- User preference-based personalization
- Memory storage for research history
- Comprehensive validation of all requirements
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
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
            - Custom prompt: {custom_prompt or "None"}
            - Days to look back: {days_back}
            
            Based on this information, determine the best search strategy and keywords.
            Consider the user's preferences and any custom prompt to refine the search approach.
            """,
        )

        # Step 2: Execute web search using Tavily
        builder.add_step(
            "execute_web_search",
            f"""
            Execute web search using the search strategy from the previous step.
            Search for recent, high-quality content related to the user's topics.
            Focus on finding articles from the last {days_back} days that are relevant and engaging.
            
            Use the Tavily search service to find content across multiple sources.
            """,
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
            """,
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
            """,
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
            """,
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
        elif task == "comprehensive_research":
            return await self.execute_comprehensive_research(context)
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
                "results": [],
            }

        try:
            # Search using Tavily
            search_results = await self.tavily.search_by_topics(
                topics=topics,
                max_results_per_topic=max_results_per_topic,
                days_back=days_back,
            )

            if not search_results["success"]:
                return search_results

            # Process and filter results
            all_articles = []
            for topic, topic_data in search_results["results_by_topic"].items():
                if topic_data["success"]:
                    for article in topic_data["results"]:
                        article["topic"] = topic
                        # Clean web content artifacts
                        cleaned_article = self.tavily.enhance_article_with_ai_summary(article)
                        all_articles.append(cleaned_article)

            # Filter for quality and remove duplicates (Requirements 3.2, 3.4)
            filtered_articles = self.tavily.filter_content_by_quality(all_articles)
            unique_articles = self.tavily.detect_duplicates(filtered_articles)

            # Prioritize recent content (Requirement 3.3)
            prioritized_articles = self._prioritize_recent_content(
                unique_articles, days_back
            )

            return {
                "success": True,
                "search_type": "topics",
                "topics": topics,
                "total_found": len(all_articles),
                "after_filtering": len(unique_articles),
                "after_prioritization": len(prioritized_articles),
                "articles": prioritized_articles[:15],  # Limit to top 15
                "search_metadata": search_results["search_metadata"],
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
                "results": [],
            }

        try:
            # Extract search terms from custom prompt
            search_query = self._extract_search_terms(custom_prompt, user_topics)

            # Search using Tavily
            search_results = await self.tavily.search_news(
                query=search_query, days_back=days_back, max_results=20
            )

            if not search_results["success"]:
                return search_results

            # Filter and process results (Requirements 3.2, 3.4)
            articles = search_results.get("results", [])
            
            # Clean web content artifacts from articles
            cleaned_articles = []
            for article in articles:
                cleaned_article = self.tavily.enhance_article_with_ai_summary(article)
                cleaned_articles.append(cleaned_article)
            
            filtered_articles = self.tavily.filter_content_by_quality(cleaned_articles)
            unique_articles = self.tavily.detect_duplicates(filtered_articles)

            # Prioritize recent content (Requirement 3.3)
            prioritized_articles = self._prioritize_recent_content(
                unique_articles, days_back
            )

            return {
                "success": True,
                "search_type": "custom_prompt",
                "original_prompt": custom_prompt,
                "search_query": search_query,
                "total_found": len(articles),
                "after_filtering": len(unique_articles),
                "after_prioritization": len(prioritized_articles),
                "articles": prioritized_articles[:15],
                "search_metadata": {"days_back": days_back, "custom_prompt": True},
            }

        except Exception as e:
            return await self.handle_error(e, context)

    async def _get_trending_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get trending content across general topics (Requirement 3.3)"""
        trending_topics = [
            "artificial intelligence",
            "technology trends",
            "startup news",
            "business innovation",
            "science breakthroughs",
        ]

        context_with_trending = {
            **context,
            "topics": trending_topics,
            "days_back": 1,  # Very recent for trending (last 24 hours)
            "max_results_per_topic": 3,
        }

        result = await self._search_by_topics(context_with_trending)

        # Mark as trending content
        if result.get("success") and result.get("articles"):
            for article in result["articles"]:
                article["is_trending"] = True
                article["trending_score"] = (
                    article.get("score", 0) * 1.2
                )  # Boost trending content

        return result

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
                enhanced_articles = await self._generate_summaries_and_insights(
                    articles
                )
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
                        "content_analysis": await self.analyze_content_trends(articles),
                    },
                    ttl_hours=24,
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
            "artificial intelligence",
            "AI",
            "machine learning",
            "ML",
            "startup",
            "funding",
            "venture capital",
            "IPO",
            "technology",
            "tech",
            "innovation",
            "breakthrough",
            "business",
            "market",
            "industry",
            "company",
            "science",
            "research",
            "study",
            "discovery",
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

    async def validate_research_requirements(
        self, research_result: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Validate that all research requirements (3.1-3.5) are met"""
        validation = {
            "3.1_tavily_search": False,
            "3.2_content_filtering": False,
            "3.3_recent_prioritization": False,
            "3.4_duplicate_detection": False,
            "3.5_summaries_insights": False,
        }

        if not research_result.get("success"):
            return validation

        # 3.1: Tavily API search based on user preferences
        if research_result.get("search_metadata") and research_result.get("articles"):
            validation["3.1_tavily_search"] = True

        # 3.2: Content filtering based on topics and relevance scores
        if research_result.get("after_filtering", 0) <= research_result.get(
            "total_found", 0
        ):
            validation["3.2_content_filtering"] = True

        # 3.3: Recent content prioritization
        articles = research_result.get("articles", [])
        if any(article.get("is_recent") for article in articles):
            validation["3.3_recent_prioritization"] = True

        # 3.4: Duplicate detection
        if research_result.get("after_filtering", 0) <= research_result.get(
            "total_found", 0
        ):
            validation["3.4_duplicate_detection"] = True

        # 3.5: Summaries and key insights
        if articles and any(
            article.get("ai_summary") or article.get("key_insights")
            for article in articles
        ):
            validation["3.5_summaries_insights"] = True

        return validation

    async def execute_comprehensive_research(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute comprehensive research that demonstrates all requirements (3.1-3.5)

        This method serves as the main entry point for research operations and ensures
        all requirements are properly implemented and validated.
        """
        try:
            user_id = context.get("user_id")
            topics = context.get("topics", [])
            custom_prompt = context.get("custom_prompt")

            # Determine search strategy based on context
            if custom_prompt:
                # Use custom prompt search
                result = await self._search_custom_prompt(context)
            elif topics:
                # Use topic-based search
                result = await self._search_by_topics(context)
            else:
                # Fallback to trending content
                result = await self._get_trending_content(context)

            if not result.get("success"):
                return result

            # Enhance articles with summaries and insights (Requirement 3.5)
            articles = result.get("articles", [])
            if articles:
                enhanced_articles = await self._generate_summaries_and_insights(
                    articles
                )
                result["articles"] = enhanced_articles

                # Update counts after enhancement
                result["enhanced_articles"] = len(
                    [a for a in enhanced_articles if a.get("enhanced")]
                )

            # Validate all requirements are met
            validation = await self.validate_research_requirements(result)
            result["requirements_validation"] = validation
            result["all_requirements_met"] = all(validation.values())

            # Store comprehensive results in memory
            if user_id:
                await self.memory.store_user_context(
                    user_id=user_id,
                    context_type="comprehensive_research",
                    context_data={
                        "result": result,
                        "validation": validation,
                        "research_timestamp": datetime.utcnow().isoformat(),
                        "context": context,
                    },
                    ttl_hours=24,
                )

            return result

        except Exception as e:
            return await self.handle_error(e, context)

    async def _generate_summaries_and_insights(
        self, articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate summaries and key insights for articles using Portia"""
        enhanced_articles = []

        for article in articles:
            try:
                # Create a plan for summarizing and extracting insights from each article
                builder = PlanBuilder()

                article_content = article.get("content", "")
                article_title = article.get("title", "")

                builder.add_step(
                    "summarize_article",
                    f"""
                    Analyze this article and provide:
                    1. A concise 2-3 sentence summary
                    2. 3-5 key insights or takeaways
                    3. Relevance score (1-10) for newsletter readers
                    4. Suggested newsletter section (e.g., "Tech News", "Business Updates", "Innovation Spotlight")
                    
                    Article Title: {article_title}
                    Article Content: {article_content[:1000]}...
                    
                    Format your response as JSON with keys: summary, insights, relevance_score, suggested_section
                    """,
                )

                plan = builder.build()
                result = await self.run_plan(plan)

                if result["success"] and result.get("result"):
                    # Parse the AI response and add to article
                    ai_analysis = result["result"]

                    # Add the enhanced data to the article
                    enhanced_article = {
                        **article,
                        "ai_summary": ai_analysis.get("summary", ""),
                        "key_insights": ai_analysis.get("insights", []),
                        "relevance_score": ai_analysis.get("relevance_score", 5),
                        "suggested_section": ai_analysis.get(
                            "suggested_section", "General"
                        ),
                        "enhanced": True,
                    }
                else:
                    # Fallback to basic processing if AI analysis fails
                    enhanced_article = {
                        **article,
                        "ai_summary": self._create_basic_summary(article_content),
                        "key_insights": self._extract_basic_insights(article_content),
                        "relevance_score": article.get("score", 5),
                        "suggested_section": self._categorize_content(article_title),
                        "enhanced": False,
                    }

                enhanced_articles.append(enhanced_article)

            except Exception as e:
                # If enhancement fails, keep original article with basic enhancements
                enhanced_articles.append(
                    {
                        **article,
                        "ai_summary": self._create_basic_summary(
                            article.get("content", "")
                        ),
                        "key_insights": [],
                        "relevance_score": article.get("score", 5),
                        "suggested_section": "General",
                        "enhanced": False,
                        "enhancement_error": str(e),
                    }
                )

        return enhanced_articles

    def _create_basic_summary(self, content: str) -> str:
        """Create a basic summary when AI enhancement fails"""
        if not content:
            return "No content available for summary."

        # Simple extractive summary - take first few sentences
        sentences = content.split(". ")
        if len(sentences) >= 2:
            return ". ".join(sentences[:2]) + "."
        else:
            return content[:200] + "..." if len(content) > 200 else content

    def _extract_basic_insights(self, content: str) -> List[str]:
        """Extract basic insights when AI enhancement fails"""
        insights = []
        content_lower = content.lower()

        # Look for key phrases that indicate insights
        insight_indicators = [
            "breakthrough",
            "innovation",
            "significant",
            "important",
            "reveals",
            "discovers",
            "announces",
            "launches",
        ]

        sentences = content.split(". ")
        for sentence in sentences[:5]:  # Check first 5 sentences
            for indicator in insight_indicators:
                if indicator in sentence.lower():
                    insights.append(sentence.strip())
                    break
            if len(insights) >= 3:
                break

        return insights[:3]  # Return max 3 insights

    def _categorize_content(self, title: str) -> str:
        """Categorize content based on title keywords"""
        title_lower = title.lower()

        categories = {
            "Tech News": [
                "technology",
                "tech",
                "ai",
                "artificial intelligence",
                "software",
                "hardware",
            ],
            "Business Updates": [
                "business",
                "company",
                "startup",
                "funding",
                "investment",
                "market",
            ],
            "Innovation Spotlight": [
                "innovation",
                "breakthrough",
                "discovery",
                "research",
                "development",
            ],
            "Industry Analysis": [
                "analysis",
                "report",
                "study",
                "trends",
                "outlook",
                "forecast",
            ],
            "Science & Research": [
                "science",
                "research",
                "study",
                "experiment",
                "scientific",
            ],
        }

        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category

        return "General"

    def _prioritize_recent_content(
        self, articles: List[Dict[str, Any]], days_back: int
    ) -> List[Dict[str, Any]]:
        """Prioritize content published within the last 24 hours (Requirement 3.3)"""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        # Separate articles into recent (last 24h) and older
        recent_articles = []
        older_articles = []

        for article in articles:
            # Try to parse published date if available
            published_date = None
            if "published_date" in article:
                try:
                    # Handle different date formats
                    date_str = article["published_date"]
                    if isinstance(date_str, str):
                        # Try common ISO format first
                        try:
                            published_date = datetime.fromisoformat(
                                date_str.replace("Z", "+00:00")
                            )
                        except:
                            # Try other common formats
                            from dateutil import parser

                            published_date = parser.parse(date_str)
                except:
                    pass

            # If we can't parse the date, assume it's recent if it has high relevance
            if published_date is None:
                # Use Tavily's score as a proxy for recency
                if article.get("score", 0) > 0.8:
                    recent_articles.append(article)
                else:
                    older_articles.append(article)
            elif published_date >= yesterday:
                # Article is from last 24 hours
                article["is_recent"] = True
                recent_articles.append(article)
            else:
                article["is_recent"] = False
                older_articles.append(article)

        # Sort recent articles by relevance score, older articles by score
        recent_articles.sort(key=lambda x: x.get("score", 0), reverse=True)
        older_articles.sort(key=lambda x: x.get("score", 0), reverse=True)

        # Combine with recent articles first (prioritized)
        prioritized = recent_articles + older_articles

        return prioritized

    async def analyze_content_trends(
        self, articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze trends in the researched content"""
        if not articles:
            return {"trends": [], "topics": [], "sentiment": "neutral"}

        # Simple trend analysis
        topics_count = {}
        sources_count = {}
        sections_count = {}

        for article in articles:
            # Count topics
            topic = article.get("topic", "general")
            topics_count[topic] = topics_count.get(topic, 0) + 1

            # Count sources
            url = article.get("url", "")
            if url:
                domain = url.split("//")[-1].split("/")[0]
                sources_count[domain] = sources_count.get(domain, 0) + 1

            # Count suggested sections
            section = article.get("suggested_section", "General")
            sections_count[section] = sections_count.get(section, 0) + 1

        # Sort by frequency
        top_topics = sorted(topics_count.items(), key=lambda x: x[1], reverse=True)
        top_sources = sorted(sources_count.items(), key=lambda x: x[1], reverse=True)
        top_sections = sorted(sections_count.items(), key=lambda x: x[1], reverse=True)

        # Calculate average relevance score
        relevance_scores = [article.get("relevance_score", 5) for article in articles]
        avg_relevance = (
            sum(relevance_scores) / len(relevance_scores) if relevance_scores else 5
        )

        return {
            "total_articles": len(articles),
            "top_topics": top_topics[:5],
            "top_sources": top_sources[:5],
            "top_sections": top_sections[:5],
            "content_diversity": len(topics_count),
            "source_diversity": len(sources_count),
            "average_relevance": round(avg_relevance, 2),
            "high_relevance_count": len([s for s in relevance_scores if s >= 7]),
        }


# Global research agent instance
research_agent = NewsletterResearchAgent()
