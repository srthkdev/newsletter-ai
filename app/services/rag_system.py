"""
RAG (Retrieval-Augmented Generation) System for Newsletter AI
Handles vector embeddings, storage, and retrieval for personalized content generation
"""
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime
from app.services.embeddings import embedding_service
from app.services.upstash import vector_service
from app.services.memory import memory_service

class RAGSystem:
    """
    Comprehensive RAG system for newsletter personalization
    Handles embedding, storage, retrieval, and context generation
    """
    
    def __init__(self):
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.memory_service = memory_service
    
    async def embed_and_store_newsletter(
        self, 
        newsletter_id: str, 
        user_id: str, 
        newsletter_data: Dict[str, Any]
    ) -> bool:
        """
        Embed newsletter content and store in vector database
        
        Args:
            newsletter_id: Unique newsletter identifier
            user_id: User identifier
            newsletter_data: Complete newsletter data
        
        Returns:
            True if successfully embedded and stored
        """
        try:
            # Extract content for embedding
            content_parts = []
            
            # Add title
            if newsletter_data.get("title"):
                content_parts.append(f"Title: {newsletter_data['title']}")
            
            # Add introduction
            if newsletter_data.get("introduction"):
                content_parts.append(f"Introduction: {newsletter_data['introduction']}")
            
            # Add section content
            sections = newsletter_data.get("sections", [])
            for section in sections:
                if isinstance(section, dict):
                    section_title = section.get("title", "")
                    articles = section.get("articles", [])
                    
                    content_parts.append(f"Section: {section_title}")
                    
                    for article in articles:
                        if isinstance(article, str):
                            content_parts.append(article[:200])  # Truncate long articles
            
            # Add conclusion
            if newsletter_data.get("conclusion"):
                content_parts.append(f"Conclusion: {newsletter_data['conclusion']}")
            
            # Combine all content
            full_content = "\n\n".join(content_parts)
            
            # Create embedding
            embedding = await self.embedding_service.create_embedding(full_content)
            if not embedding:
                return False
            
            # Prepare metadata
            metadata = {
                "newsletter_id": newsletter_id,
                "user_id": user_id,
                "type": "newsletter",
                "generated_at": newsletter_data.get("generated_at", datetime.utcnow().isoformat()),
                "article_count": newsletter_data.get("metadata", {}).get("article_count", 0),
                "tone": newsletter_data.get("metadata", {}).get("user_preferences", {}).get("tone", "professional"),
                "topics": json.dumps(newsletter_data.get("metadata", {}).get("user_preferences", {}).get("topics", [])),
                "custom_prompt": newsletter_data.get("metadata", {}).get("custom_prompt", ""),
                "word_count": len(full_content.split()),
                "content_preview": full_content[:200]
            }
            
            # Store in vector database
            vector_data = {
                "id": f"newsletter_{newsletter_id}_{user_id}",
                "values": embedding,
                "metadata": metadata
            }
            
            return await self.vector_service.upsert([vector_data])
        
        except Exception as e:
            print(f"Failed to embed and store newsletter: {e}")
            return False
    
    async def retrieve_similar_newsletters(
        self, 
        user_id: str, 
        query: str, 
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar newsletters from user's history
        
        Args:
            user_id: User identifier
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of similar newsletters with metadata
        """
        try:
            # Create query embedding
            query_embedding = await self.embedding_service.create_embedding(query)
            if not query_embedding:
                return []
            
            # Search with user filter
            filter_criteria = {"user_id": user_id, "type": "newsletter"}
            
            results = await self.vector_service.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_criteria
            )
            
            # Filter by similarity threshold and format results
            similar_newsletters = []
            for match in results:
                if match.score >= similarity_threshold:
                    similar_newsletters.append({
                        "newsletter_id": match.metadata.get("newsletter_id"),
                        "similarity_score": match.score,
                        "generated_at": match.metadata.get("generated_at"),
                        "tone": match.metadata.get("tone"),
                        "topics": json.loads(match.metadata.get("topics", "[]")),
                        "article_count": match.metadata.get("article_count", 0),
                        "content_preview": match.metadata.get("content_preview", ""),
                        "custom_prompt": match.metadata.get("custom_prompt", "")
                    })
            
            return similar_newsletters
        
        except Exception as e:
            print(f"Failed to retrieve similar newsletters: {e}")
            return []
    
    async def get_content_recommendations(
        self, 
        user_id: str, 
        current_topics: List[str],
        current_articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get content recommendations based on user's reading history
        
        Args:
            user_id: User identifier
            current_topics: Topics for current newsletter
            current_articles: Articles being included
        
        Returns:
            Dictionary with recommendations and insights
        """
        try:
            recommendations = {
                "topic_suggestions": [],
                "tone_recommendations": {},
                "content_insights": [],
                "personalization_level": "basic"
            }
            
            # Create query from current content
            article_titles = [article.get("title", "") for article in current_articles[:3]]
            query = f"newsletter about {', '.join(current_topics)} covering {', '.join(article_titles)}"
            
            # Get similar newsletters
            similar_newsletters = await self.retrieve_similar_newsletters(
                user_id=user_id,
                query=query,
                top_k=10,
                similarity_threshold=0.6
            )
            
            if not similar_newsletters:
                return recommendations
            
            # Analyze patterns in similar newsletters
            tone_counts = {}
            topic_frequency = {}
            
            for newsletter in similar_newsletters:
                # Count tone preferences
                tone = newsletter.get("tone", "professional")
                tone_counts[tone] = tone_counts.get(tone, 0) + 1
                
                # Count topic frequency
                topics = newsletter.get("topics", [])
                for topic in topics:
                    topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
            
            # Generate recommendations
            if tone_counts:
                preferred_tone = max(tone_counts, key=tone_counts.get)
                recommendations["tone_recommendations"] = {
                    "preferred_tone": preferred_tone,
                    "confidence": tone_counts[preferred_tone] / len(similar_newsletters),
                    "alternatives": list(tone_counts.keys())
                }
            
            # Topic suggestions based on frequency
            if topic_frequency:
                sorted_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)
                recommendations["topic_suggestions"] = [
                    {"topic": topic, "frequency": freq, "relevance": freq / len(similar_newsletters)}
                    for topic, freq in sorted_topics[:5]
                ]
            
            # Content insights
            recommendations["content_insights"] = [
                f"You've shown interest in {len(set(topic_frequency.keys()))} different topics",
                f"Your most engaging newsletters had {sum(n.get('article_count', 0) for n in similar_newsletters[:3]) // 3} articles on average",
                f"Based on {len(similar_newsletters)} similar newsletters in your history"
            ]
            
            recommendations["personalization_level"] = "high" if len(similar_newsletters) >= 3 else "medium"
            
            return recommendations
        
        except Exception as e:
            print(f"Failed to get content recommendations: {e}")
            return {
                "topic_suggestions": [],
                "tone_recommendations": {},
                "content_insights": [],
                "personalization_level": "basic"
            }
    
    async def analyze_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze user preferences based on newsletter history
        
        Args:
            user_id: User identifier
        
        Returns:
            Analysis of user preferences and patterns
        """
        try:
            # Get all user newsletters from vector database
            all_newsletters = await self.retrieve_similar_newsletters(
                user_id=user_id,
                query="newsletter content analysis",
                top_k=50,
                similarity_threshold=0.0  # Get all newsletters
            )
            
            if not all_newsletters:
                return {"analysis": "No newsletter history available", "patterns": {}}
            
            # Analyze patterns
            analysis = {
                "total_newsletters": len(all_newsletters),
                "preferred_tones": {},
                "topic_interests": {},
                "content_patterns": {},
                "engagement_insights": []
            }
            
            # Analyze tone preferences
            for newsletter in all_newsletters:
                tone = newsletter.get("tone", "professional")
                analysis["preferred_tones"][tone] = analysis["preferred_tones"].get(tone, 0) + 1
            
            # Analyze topic interests
            for newsletter in all_newsletters:
                topics = newsletter.get("topics", [])
                for topic in topics:
                    analysis["topic_interests"][topic] = analysis["topic_interests"].get(topic, 0) + 1
            
            # Content patterns
            article_counts = [n.get("article_count", 0) for n in all_newsletters]
            if article_counts:
                analysis["content_patterns"] = {
                    "avg_articles_per_newsletter": sum(article_counts) / len(article_counts),
                    "preferred_length": "short" if sum(article_counts) / len(article_counts) < 5 else "long",
                    "consistency_score": 1.0 - (max(article_counts) - min(article_counts)) / max(article_counts, 1)
                }
            
            # Generate insights
            if analysis["preferred_tones"]:
                most_used_tone = max(analysis["preferred_tones"], key=analysis["preferred_tones"].get)
                analysis["engagement_insights"].append(f"Prefers {most_used_tone} tone in newsletters")
            
            if analysis["topic_interests"]:
                top_topics = sorted(analysis["topic_interests"].items(), key=lambda x: x[1], reverse=True)[:3]
                analysis["engagement_insights"].append(f"Most interested in: {', '.join([t[0] for t in top_topics])}")
            
            return analysis
        
        except Exception as e:
            print(f"Failed to analyze user preferences: {e}")
            return {"analysis": f"Analysis failed: {e}", "patterns": {}}
    
    async def generate_personalized_content_context(
        self, 
        user_id: str, 
        articles: List[Dict[str, Any]], 
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive context for personalized content generation
        
        Args:
            user_id: User identifier
            articles: Current articles to include
            user_preferences: User's stated preferences
        
        Returns:
            Comprehensive context for content generation
        """
        try:
            context = {
                "rag_available": False,
                "similar_content": [],
                "recommendations": {},
                "personalization_insights": [],
                "content_strategy": {}
            }
            
            # Get current topics
            topics = user_preferences.get("topics", [])
            
            # Get content recommendations
            recommendations = await self.get_content_recommendations(
                user_id=user_id,
                current_topics=topics,
                current_articles=articles
            )
            
            context["recommendations"] = recommendations
            context["rag_available"] = recommendations.get("personalization_level") != "basic"
            
            # Get similar content
            if topics:
                query = f"newsletter about {', '.join(topics)}"
                similar_content = await self.retrieve_similar_newsletters(
                    user_id=user_id,
                    query=query,
                    top_k=5
                )
                context["similar_content"] = similar_content
            
            # Generate personalization insights
            if context["rag_available"]:
                context["personalization_insights"] = [
                    "Using your reading history to personalize content",
                    f"Found {len(context['similar_content'])} similar newsletters in your history",
                    f"Personalization level: {recommendations.get('personalization_level', 'basic')}"
                ]
            
            # Content strategy based on analysis
            user_analysis = await self.analyze_user_preferences(user_id)
            context["content_strategy"] = {
                "recommended_tone": recommendations.get("tone_recommendations", {}).get("preferred_tone", user_preferences.get("tone", "professional")),
                "optimal_article_count": user_analysis.get("content_patterns", {}).get("avg_articles_per_newsletter", 5),
                "focus_topics": [t["topic"] for t in recommendations.get("topic_suggestions", [])[:3]]
            }
            
            return context
        
        except Exception as e:
            print(f"Failed to generate personalized content context: {e}")
            return {
                "rag_available": False,
                "similar_content": [],
                "recommendations": {},
                "personalization_insights": [f"Personalization failed: {e}"],
                "content_strategy": {}
            }

# Global RAG system instance
rag_system = RAGSystem()