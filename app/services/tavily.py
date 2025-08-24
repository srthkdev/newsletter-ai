"""
Tavily API integration for web search functionality
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
from app.core.config import settings


class TavilyService:
    """Service for web search using Tavily API"""

    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com"
        self.timeout = 30

    async def search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 10,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        include_raw_content: bool = False,
        include_images: bool = False,
    ) -> Dict[str, Any]:
        """
        Search for content using Tavily API

        Args:
            query: Search query string
            search_depth: "basic" or "advanced" search depth
            max_results: Maximum number of results to return
            include_domains: List of domains to include in search
            exclude_domains: List of domains to exclude from search
            include_raw_content: Whether to include raw HTML content
            include_images: Whether to include images in results

        Returns:
            Dictionary containing search results and metadata
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Tavily API key not configured",
                "results": [],
            }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": search_depth,
                    "max_results": max_results,
                    "include_raw_content": include_raw_content,
                    "include_images": include_images,
                }

                if include_domains:
                    payload["include_domains"] = include_domains

                if exclude_domains:
                    payload["exclude_domains"] = exclude_domains

                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "query": query,
                        "results": data.get("results", []),
                        "answer": data.get("answer", ""),
                        "follow_up_questions": data.get("follow_up_questions", []),
                        "search_metadata": {
                            "search_depth": search_depth,
                            "max_results": max_results,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Tavily API error: {response.status_code} - {response.text}",
                        "results": [],
                    }

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Tavily API request timed out",
                "results": [],
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Tavily API error: {str(e)}",
                "results": [],
            }

    async def search_news(
        self, query: str, days_back: int = 7, max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search for recent news articles

        Args:
            query: Search query for news
            days_back: Number of days to look back for news
            max_results: Maximum number of results

        Returns:
            Dictionary containing news search results
        """
        # Add time constraint to query for recent news
        time_query = f"{query} after:{(datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')}"

        return await self.search(
            query=time_query,
            search_depth="advanced",
            max_results=max_results,
            include_domains=[
                "techcrunch.com",
                "reuters.com",
                "bloomberg.com",
                "wired.com",
                "theverge.com",
                "arstechnica.com",
                "venturebeat.com",
                "businessinsider.com",
            ],
        )

    async def search_by_topics(
        self, topics: List[str], max_results_per_topic: int = 5, days_back: int = 3
    ) -> Dict[str, Any]:
        """
        Search for content across multiple topics

        Args:
            topics: List of topics to search for
            max_results_per_topic: Maximum results per topic
            days_back: Number of days to look back

        Returns:
            Dictionary with results organized by topic
        """
        all_results = {}

        for topic in topics:
            topic_results = await self.search_news(
                query=topic, days_back=days_back, max_results=max_results_per_topic
            )

            all_results[topic] = {
                "success": topic_results["success"],
                "results": topic_results.get("results", []),
                "count": len(topic_results.get("results", [])),
            }

        return {
            "success": True,
            "topics": topics,
            "results_by_topic": all_results,
            "total_results": sum(
                len(topic_data.get("results", []))
                for topic_data in all_results.values()
            ),
            "search_metadata": {
                "days_back": days_back,
                "max_results_per_topic": max_results_per_topic,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

    def filter_content_by_quality(
        self, results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter search results by content quality indicators

        Args:
            results: List of search results from Tavily

        Returns:
            Filtered list of high-quality results
        """
        filtered_results = []

        for result in results:
            # Quality indicators
            has_good_title = len(result.get("title", "")) > 10
            has_content = len(result.get("content", "")) > 100
            has_recent_date = True  # Tavily already filters by recency

            # Score based on content length and title quality
            content_length = len(result.get("content", ""))
            title_length = len(result.get("title", ""))

            quality_score = 0
            if content_length > 200:
                quality_score += 2
            elif content_length > 100:
                quality_score += 1

            if title_length > 20:
                quality_score += 1

            if result.get("score", 0) > 0.7:  # Tavily relevance score
                quality_score += 2

            # Only include results with minimum quality
            if quality_score >= 2 and has_good_title and has_content:
                result["quality_score"] = quality_score
                filtered_results.append(result)

        # Sort by quality score and Tavily relevance score
        filtered_results.sort(
            key=lambda x: (x.get("quality_score", 0), x.get("score", 0)), reverse=True
        )

        return filtered_results

    def clean_web_content(self, content: str) -> str:
        """
        Clean web content by removing navigation, ads, image references, and other artifacts
        
        Args:
            content: Raw web content from Tavily
            
        Returns:
            Cleaned content suitable for newsletter display
        """
        if not content:
            return ""
            
        import re
        
        # Remove common web navigation and UI elements
        patterns_to_remove = [
            r'skip to main content',
            r'report this ad',
            r'exclusive news, data and analytics for financial market professionals',
            r'learn more about refinitiv',
            r'stay informed[-\s]*',
            r'© \d{4} reuters',
            r'all rights reserved',
            r'download the app \([^)]+\)',
            r'newsletters\s*subscribe',
            r'information you can trust[-\s]*',
            r'opens new tab',
            r'image \d+:?[^.]*',
            r'image \d+',
            r'\[\.\.\.\.?\]',
            r'advertisement',
            r'cookie policy',
            r'privacy policy',
            r'terms of service',
            r'follow us on',
            r'share this article',
            r'related articles?',
            r'trending now',
            r'most popular',
            r'subscribe to',
            r'sign up for',
            r'\bads?\b',
            r'sponsored content',
            r'partner content'
        ]
        
        cleaned = content
        
        # Remove patterns (case insensitive)
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove HTML tags and entities
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        cleaned = re.sub(r'&[a-zA-Z]+;', '', cleaned)
        
        # Remove multiple consecutive punctuation
        cleaned = re.sub(r'[.]{3,}', '...', cleaned)
        cleaned = re.sub(r'[-]{3,}', '---', cleaned)
        
        # Remove URLs
        cleaned = re.sub(r'https?://[^\s]+', '', cleaned)
        
        # Remove email addresses
        cleaned = re.sub(r'\S+@\S+\.\S+', '', cleaned)
        
        # Remove extra whitespace and clean up
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        # Remove lines that are mostly non-alphabetic
        lines = cleaned.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) < 10:  # Skip very short lines
                continue
                
            # Check if line has reasonable amount of alphabetic characters
            alpha_count = sum(1 for c in line if c.isalpha())
            if alpha_count / len(line) >= 0.5:  # At least 50% letters
                filtered_lines.append(line)
        
        cleaned = '\n'.join(filtered_lines)
        
        # Final cleanup
        cleaned = cleaned.strip()
        
        return cleaned
        
    def enhance_article_with_ai_summary(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance article with AI-generated summary, removing raw web content
        
        Args:
            article: Article dictionary from Tavily
            
        Returns:
            Enhanced article with cleaned content and AI summary
        """
        enhanced_article = article.copy()
        
        # Clean the content
        raw_content = article.get('content', '')
        cleaned_content = self.clean_web_content(raw_content)
        
        enhanced_article['content'] = cleaned_content
        enhanced_article['original_content_length'] = len(raw_content)
        enhanced_article['cleaned_content_length'] = len(cleaned_content)
        
        # Generate AI summary (this would be called by writing agent)
        enhanced_article['needs_ai_summary'] = True
        enhanced_article['summary_prompt'] = f"Summarize this article about {article.get('title', 'news')}: {cleaned_content[:500]}..."
        
        return enhanced_article

    def detect_duplicates(
        self, results: List[Dict[str, Any]], title_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Detect and remove duplicate articles based on title similarity
        
        Args:
            results: List of search results
            title_threshold: Similarity threshold for title comparison
            
        Returns:
            List of unique articles with duplicates removed
        """
        if not results:
            return []
            
        unique_results = []
        seen_titles = []
        
        for result in results:
            title = result.get("title", "")
            if not title:
                continue
                
            is_duplicate = False
            for seen_title in seen_titles:
                if self._titles_similar(title, seen_title, title_threshold):
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                unique_results.append(result)
                seen_titles.append(title)
                
        return unique_results

    def _titles_similar(self, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """
        Check if two titles are similar using simple word overlap

        Args:
            title1: First title
            title2: Second title
            threshold: Similarity threshold (0-1)

        Returns:
            True if titles are similar
        """
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())

        if not words1 or not words2:
            return False

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        similarity = len(intersection) / len(union) if union else 0
        return similarity >= threshold


# Global Tavily service instance
tavily_service = TavilyService()
