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
        self.api_key = os.getenv('TAVILY_API_KEY')
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
        include_images: bool = False
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
                "results": []
            }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": search_depth,
                    "max_results": max_results,
                    "include_raw_content": include_raw_content,
                    "include_images": include_images
                }
                
                if include_domains:
                    payload["include_domains"] = include_domains
                
                if exclude_domains:
                    payload["exclude_domains"] = exclude_domains
                
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload,
                    headers={"Content-Type": "application/json"}
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
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Tavily API error: {response.status_code} - {response.text}",
                        "results": []
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Tavily API request timed out",
                "results": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Tavily API error: {str(e)}",
                "results": []
            }
    
    async def search_news(
        self,
        query: str,
        days_back: int = 7,
        max_results: int = 10
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
                "businessinsider.com"
            ]
        )
    
    async def search_by_topics(
        self,
        topics: List[str],
        max_results_per_topic: int = 5,
        days_back: int = 3
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
                query=topic,
                days_back=days_back,
                max_results=max_results_per_topic
            )
            
            all_results[topic] = {
                "success": topic_results["success"],
                "results": topic_results.get("results", []),
                "count": len(topic_results.get("results", []))
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
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def filter_content_by_quality(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
            key=lambda x: (x.get("quality_score", 0), x.get("score", 0)),
            reverse=True
        )
        
        return filtered_results
    
    def detect_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate content from search results
        
        Args:
            results: List of search results
        
        Returns:
            List with duplicates removed
        """
        seen_titles = set()
        seen_urls = set()
        unique_results = []
        
        for result in results:
            title = result.get("title", "").lower().strip()
            url = result.get("url", "")
            
            # Skip if we've seen this title or URL before
            if title in seen_titles or url in seen_urls:
                continue
            
            # Check for similar titles (basic similarity)
            is_similar = False
            for seen_title in seen_titles:
                if self._titles_similar(title, seen_title):
                    is_similar = True
                    break
            
            if not is_similar:
                seen_titles.add(title)
                seen_urls.add(url)
                unique_results.append(result)
        
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