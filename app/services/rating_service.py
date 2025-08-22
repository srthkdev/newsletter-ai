"""
Newsletter Rating Service
Handles rating storage, analysis, and integration with RAG system for preference learning
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from app.core.database import get_db
from app.models.rating import NewsletterRating
from app.models.user import User
from app.schemas.rating import (
    NewsletterRatingCreate, 
    NewsletterRatingUpdate, 
    NewsletterRatingStats,
    RatingAnalytics
)
from app.services.rag_system import rag_system
from app.services.memory import memory_service


class NewsletterRatingService:
    """Service for managing newsletter ratings and learning user preferences"""
    
    def __init__(self):
        self.rag_system = rag_system
        self.memory_service = memory_service
    
    async def create_rating(
        self, 
        user_id: str, 
        rating_data: NewsletterRatingCreate,
        newsletter_metadata: Optional[Dict[str, Any]] = None
    ) -> NewsletterRating:
        """Create a new newsletter rating and update user preferences"""
        
        db = next(get_db())
        try:
            # Check if rating already exists
            existing_rating = db.query(NewsletterRating).filter(
                and_(
                    NewsletterRating.user_id == user_id,
                    NewsletterRating.newsletter_id == rating_data.newsletter_id
                )
            ).first()
            
            if existing_rating:
                # Update existing rating
                return await self.update_rating(existing_rating.id, rating_data)
            
            # Create new rating
            rating = NewsletterRating(
                user_id=user_id,
                newsletter_id=rating_data.newsletter_id,
                overall_rating=rating_data.overall_rating,
                content_quality=rating_data.content_quality,
                relevance_score=rating_data.relevance_score,
                readability_score=rating_data.readability_score,
                feedback_text=rating_data.feedback_text,
                liked_topics=rating_data.liked_topics,
                disliked_topics=rating_data.disliked_topics,
                suggested_topics=rating_data.suggested_topics,
                read_time_minutes=rating_data.read_time_minutes,
                clicked_links=rating_data.clicked_links,
                shared=rating_data.shared,
                bookmarked=rating_data.bookmarked,
                preferred_tone=rating_data.preferred_tone,
                preferred_length=rating_data.preferred_length,
                preferred_frequency=rating_data.preferred_frequency,
                newsletter_metadata=newsletter_metadata,
                user_context=await self._get_user_context(user_id)
            )
            
            db.add(rating)
            db.commit()
            db.refresh(rating)
            
            # Process rating for preference learning (async)
            asyncio.create_task(self._process_rating_for_learning(rating))
            
            return rating
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def update_rating(
        self, 
        rating_id: int, 
        rating_data: NewsletterRatingUpdate
    ) -> Optional[NewsletterRating]:
        """Update an existing rating"""
        
        db = next(get_db())
        try:
            rating = db.query(NewsletterRating).filter(
                NewsletterRating.id == rating_id
            ).first()
            
            if not rating:
                return None
            
            # Update fields that are provided
            update_data = rating_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(rating, field, value)
            
            rating.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(rating)
            
            # Reprocess for learning
            asyncio.create_task(self._process_rating_for_learning(rating))
            
            return rating
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def get_user_ratings(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> List[NewsletterRating]:
        """Get user's rating history"""
        
        db = next(get_db())
        try:
            return db.query(NewsletterRating).filter(
                NewsletterRating.user_id == user_id
            ).order_by(desc(NewsletterRating.created_at)).limit(limit).all()
        finally:
            db.close()
    
    async def get_rating_stats(self, user_id: str) -> NewsletterRatingStats:
        """Get comprehensive rating statistics for a user"""
        
        db = next(get_db())
        try:
            ratings = db.query(NewsletterRating).filter(
                NewsletterRating.user_id == user_id
            ).all()
            
            if not ratings:
                return self._empty_stats()
            
            # Calculate basic stats
            total_ratings = len(ratings)
            overall_ratings = [r.overall_rating for r in ratings]
            average_rating = sum(overall_ratings) / len(overall_ratings)
            
            # Rating distribution
            rating_distribution = dict(Counter(overall_ratings))
            rating_distribution = {str(k): v for k, v in rating_distribution.items()}
            
            # Quality metrics
            content_qualities = [r.content_quality for r in ratings if r.content_quality]
            relevance_scores = [r.relevance_score for r in ratings if r.relevance_score]
            readability_scores = [r.readability_score for r in ratings if r.readability_score]
            engagement_scores = [r.engagement_score for r in ratings]
            
            # Topic analysis
            liked_topics = []
            disliked_topics = []
            suggested_topics = []
            
            for rating in ratings:
                if rating.liked_topics:
                    liked_topics.extend(rating.liked_topics)
                if rating.disliked_topics:
                    disliked_topics.extend(rating.disliked_topics)
                if rating.suggested_topics:
                    suggested_topics.extend(rating.suggested_topics)
            
            # Behavioral metrics
            read_times = [r.read_time_minutes for r in ratings if r.read_time_minutes]
            total_clicks = sum(len(r.clicked_links or []) for r in ratings)
            share_count = sum(1 for r in ratings if r.shared)
            bookmark_count = sum(1 for r in ratings if r.bookmarked)
            
            # Preference distributions
            tone_prefs = [r.preferred_tone for r in ratings if r.preferred_tone]
            length_prefs = [r.preferred_length for r in ratings if r.preferred_length]
            freq_prefs = [r.preferred_frequency for r in ratings if r.preferred_frequency]
            
            return NewsletterRatingStats(
                total_ratings=total_ratings,
                average_rating=average_rating,
                rating_distribution=rating_distribution,
                average_content_quality=sum(content_qualities) / len(content_qualities) if content_qualities else None,
                average_relevance=sum(relevance_scores) / len(relevance_scores) if relevance_scores else None,
                average_readability=sum(readability_scores) / len(readability_scores) if readability_scores else None,
                average_engagement=sum(engagement_scores) / len(engagement_scores),
                most_liked_topics=self._count_topics(liked_topics),
                most_disliked_topics=self._count_topics(disliked_topics),
                suggested_topics=self._count_topics(suggested_topics),
                average_read_time=sum(read_times) / len(read_times) if read_times else None,
                link_click_rate=total_clicks / total_ratings if total_ratings > 0 else 0,
                share_rate=share_count / total_ratings if total_ratings > 0 else 0,
                bookmark_rate=bookmark_count / total_ratings if total_ratings > 0 else 0,
                preferred_tone_distribution=dict(Counter(tone_prefs)),
                preferred_length_distribution=dict(Counter(length_prefs)),
                preferred_frequency_distribution=dict(Counter(freq_prefs))
            )
            
        finally:
            db.close()
    
    async def get_rating_analytics(self, user_id: str) -> RatingAnalytics:
        """Get advanced analytics and insights from user ratings"""
        
        rating_stats = await self.get_rating_stats(user_id)
        
        # Generate improvement suggestions
        improvement_suggestions = await self._generate_improvement_suggestions(user_id, rating_stats)
        
        # Generate personalization insights
        personalization_insights = await self._generate_personalization_insights(user_id, rating_stats)
        
        # Calculate engagement trends
        engagement_trends = await self._calculate_engagement_trends(user_id)
        
        # Calculate topic preferences
        topic_preferences = await self._calculate_topic_preferences(user_id, rating_stats)
        
        return RatingAnalytics(
            user_id=user_id,
            rating_summary=rating_stats,
            improvement_suggestions=improvement_suggestions,
            personalization_insights=personalization_insights,
            engagement_trends=engagement_trends,
            topic_preferences=topic_preferences
        )
    
    async def learn_preferences_from_ratings(self, user_id: str) -> Dict[str, Any]:
        """Learn and update user preferences based on rating history"""
        
        db = next(get_db())
        try:
            ratings = db.query(NewsletterRating).filter(
                NewsletterRating.user_id == user_id
            ).order_by(desc(NewsletterRating.created_at)).limit(50).all()
            
            if not ratings:
                return {"updated": False, "reason": "No ratings found"}
            
            # Analyze rating patterns
            learned_preferences = await self._analyze_rating_patterns(ratings)
            
            # Update user preferences in RAG system
            await self._update_rag_preferences(user_id, learned_preferences)
            
            # Store learning insights in memory
            await self.memory_service.store_user_context(
                user_id=str(user_id),
                context_key="rating_learned_preferences",
                context_data={
                    "learned_preferences": learned_preferences,
                    "analyzed_ratings": len(ratings),
                    "last_update": datetime.utcnow().isoformat()
                }
            )
            
            return {
                "updated": True,
                "learned_preferences": learned_preferences,
                "ratings_analyzed": len(ratings)
            }
            
        finally:
            db.close()
    
    async def get_newsletter_rating(
        self, 
        user_id: str, 
        newsletter_id: str
    ) -> Optional[NewsletterRating]:
        """Get specific newsletter rating"""
        
        db = next(get_db())
        try:
            return db.query(NewsletterRating).filter(
                and_(
                    NewsletterRating.user_id == user_id,
                    NewsletterRating.newsletter_id == newsletter_id
                )
            ).first()
        finally:
            db.close()
    
    # Private helper methods
    
    async def _process_rating_for_learning(self, rating: NewsletterRating):
        """Process a rating for immediate preference learning"""
        try:
            # Update RAG system with rating data
            await self._embed_rating_for_rag(rating)
            
            # Update preference scores
            await self._update_preference_scores(rating)
            
            # If rating is very high or low, trigger immediate preference update
            if rating.overall_rating >= 5 or rating.overall_rating <= 2:
                await self.learn_preferences_from_ratings(rating.user_id)
                
        except Exception as e:
            print(f"Error processing rating for learning: {e}")
    
    async def _embed_rating_for_rag(self, rating: NewsletterRating):
        """Embed rating data for RAG retrieval"""
        try:
            # Create embedding text from rating
            rating_text = self._create_rating_embedding_text(rating)
            
            # Store in RAG system
            await self.rag_system.embed_and_store_newsletter(
                newsletter_id=f"rating_{rating.id}",
                user_id=str(rating.user_id),
                newsletter_data={
                    "type": "rating",
                    "content": rating_text,
                    "rating": rating.overall_rating,
                    "engagement_score": rating.engagement_score,
                    "liked_topics": rating.liked_topics,
                    "disliked_topics": rating.disliked_topics,
                    "metadata": rating.newsletter_metadata
                }
            )
        except Exception as e:
            print(f"Failed to embed rating for RAG: {e}")
    
    def _create_rating_embedding_text(self, rating: NewsletterRating) -> str:
        """Create text representation of rating for embedding"""
        parts = [
            f"Rating: {rating.overall_rating}/5 stars"
        ]
        
        if rating.feedback_text:
            parts.append(f"Feedback: {rating.feedback_text}")
        
        if rating.liked_topics:
            parts.append(f"Liked topics: {', '.join(rating.liked_topics)}")
        
        if rating.disliked_topics:
            parts.append(f"Disliked topics: {', '.join(rating.disliked_topics)}")
        
        if rating.preferred_tone:
            parts.append(f"Preferred tone: {rating.preferred_tone}")
        
        return " | ".join(parts)
    
    async def _update_preference_scores(self, rating: NewsletterRating):
        """Update preference scores based on rating"""
        try:
            # Update topic preferences
            if rating.liked_topics:
                for topic in rating.liked_topics:
                    await self.memory_service.update_user_preference_score(
                        user_id=str(rating.user_id),
                        preference_type="topic",
                        preference_value=topic,
                        score_change=rating.overall_rating / 5.0
                    )
            
            if rating.disliked_topics:
                for topic in rating.disliked_topics:
                    await self.memory_service.update_user_preference_score(
                        user_id=str(rating.user_id),
                        preference_type="topic",
                        preference_value=topic,
                        score_change=-(5 - rating.overall_rating) / 5.0
                    )
            
            # Update tone preferences
            if rating.preferred_tone:
                await self.memory_service.update_user_preference_score(
                    user_id=str(rating.user_id),
                    preference_type="tone",
                    preference_value=rating.preferred_tone,
                    score_change=rating.overall_rating / 5.0
                )
                
        except Exception as e:
            print(f"Failed to update preference scores: {e}")
    
    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get current user context for rating"""
        try:
            return await self.memory_service.get_user_context(str(user_id)) or {}
        except:
            return {}
    
    def _count_topics(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Count and sort topics by frequency"""
        if not topics:
            return []
        
        topic_counts = Counter(topics)
        return [
            {"topic": topic, "count": count}
            for topic, count in topic_counts.most_common(10)
        ]
    
    def _empty_stats(self) -> NewsletterRatingStats:
        """Return empty stats object"""
        return NewsletterRatingStats(
            total_ratings=0,
            average_rating=0.0,
            rating_distribution={},
            average_content_quality=None,
            average_relevance=None,
            average_readability=None,
            average_engagement=0.0,
            most_liked_topics=[],
            most_disliked_topics=[],
            suggested_topics=[],
            average_read_time=None,
            link_click_rate=0.0,
            share_rate=0.0,
            bookmark_rate=0.0,
            preferred_tone_distribution={},
            preferred_length_distribution={},
            preferred_frequency_distribution={}
        )
    
    async def _generate_improvement_suggestions(
        self, 
        user_id: str, 
        stats: NewsletterRatingStats
    ) -> List[str]:
        """Generate improvement suggestions based on rating patterns"""
        suggestions = []
        
        if stats.average_rating < 3.0:
            suggestions.append("Consider adjusting newsletter topics based on your interests")
        
        if stats.average_relevance and stats.average_relevance < 3.0:
            suggestions.append("We'll focus more on topics that match your preferences")
        
        if stats.most_disliked_topics:
            disliked = [t["topic"] for t in stats.most_disliked_topics[:2]]
            suggestions.append(f"We'll reduce coverage of: {', '.join(disliked)}")
        
        if stats.suggested_topics:
            suggested = [t["topic"] for t in stats.suggested_topics[:2]]
            suggestions.append(f"We'll add more content about: {', '.join(suggested)}")
        
        if stats.link_click_rate < 0.1:
            suggestions.append("We'll include more actionable content with relevant links")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def _generate_personalization_insights(
        self, 
        user_id: str, 
        stats: NewsletterRatingStats
    ) -> List[str]:
        """Generate personalization insights"""
        insights = []
        
        if stats.most_liked_topics:
            liked = [t["topic"] for t in stats.most_liked_topics[:3]]
            insights.append(f"You consistently enjoy content about: {', '.join(liked)}")
        
        if stats.average_engagement > 0.7:
            insights.append("You're highly engaged with our newsletters!")
        
        if stats.preferred_tone_distribution:
            top_tone = max(stats.preferred_tone_distribution.items(), key=lambda x: x[1])
            insights.append(f"You prefer a {top_tone[0]} tone in newsletters")
        
        if stats.average_read_time and stats.average_read_time > 5:
            insights.append("You thoroughly read newsletters - we'll include more in-depth content")
        
        return insights
    
    async def _calculate_engagement_trends(self, user_id: str) -> Dict[str, Any]:
        """Calculate engagement trends over time"""
        db = next(get_db())
        try:
            # Get ratings from last 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            recent_ratings = db.query(NewsletterRating).filter(
                and_(
                    NewsletterRating.user_id == user_id,
                    NewsletterRating.created_at >= cutoff_date
                )
            ).order_by(NewsletterRating.created_at).all()
            
            if len(recent_ratings) < 2:
                return {"trend": "insufficient_data"}
            
            # Calculate trend
            early_ratings = recent_ratings[:len(recent_ratings)//2]
            late_ratings = recent_ratings[len(recent_ratings)//2:]
            
            early_avg = sum(r.overall_rating for r in early_ratings) / len(early_ratings)
            late_avg = sum(r.overall_rating for r in late_ratings) / len(late_ratings)
            
            trend = "improving" if late_avg > early_avg else "declining" if late_avg < early_avg else "stable"
            
            return {
                "trend": trend,
                "early_average": early_avg,
                "late_average": late_avg,
                "change": late_avg - early_avg,
                "data_points": len(recent_ratings)
            }
            
        finally:
            db.close()
    
    async def _calculate_topic_preferences(
        self, 
        user_id: str, 
        stats: NewsletterRatingStats
    ) -> Dict[str, float]:
        """Calculate topic preference scores"""
        preferences = {}
        
        # Positive preferences from liked topics
        for topic_data in stats.most_liked_topics:
            topic = topic_data["topic"]
            count = topic_data["count"]
            # Score based on frequency and implicit rating
            preferences[topic] = min(1.0, count / max(1, stats.total_ratings) * 2)
        
        # Negative preferences from disliked topics
        for topic_data in stats.most_disliked_topics:
            topic = topic_data["topic"]
            count = topic_data["count"]
            # Negative score
            preferences[topic] = max(-1.0, -count / max(1, stats.total_ratings) * 2)
        
        return preferences
    
    async def _analyze_rating_patterns(
        self, 
        ratings: List[NewsletterRating]
    ) -> Dict[str, Any]:
        """Analyze patterns in user ratings to learn preferences"""
        
        # High-rated content analysis
        high_rated = [r for r in ratings if r.overall_rating >= 4]
        low_rated = [r for r in ratings if r.overall_rating <= 2]
        
        patterns = {
            "high_rated_patterns": {},
            "low_rated_patterns": {},
            "tone_preferences": {},
            "length_preferences": {},
            "topic_preferences": {}
        }
        
        # Analyze high-rated content
        if high_rated:
            patterns["high_rated_patterns"] = {
                "count": len(high_rated),
                "common_topics": self._extract_common_elements([r.liked_topics for r in high_rated if r.liked_topics]),
                "preferred_tones": [r.preferred_tone for r in high_rated if r.preferred_tone],
                "average_engagement": sum(r.engagement_score for r in high_rated) / len(high_rated)
            }
        
        # Analyze low-rated content
        if low_rated:
            patterns["low_rated_patterns"] = {
                "count": len(low_rated),
                "problem_topics": self._extract_common_elements([r.disliked_topics for r in low_rated if r.disliked_topics]),
                "avoided_tones": [r.preferred_tone for r in low_rated if r.preferred_tone]
            }
        
        return patterns
    
    def _extract_common_elements(self, lists: List[List[str]]) -> List[str]:
        """Extract common elements from lists"""
        if not lists:
            return []
        
        all_elements = []
        for lst in lists:
            if lst:
                all_elements.extend(lst)
        
        if not all_elements:
            return []
        
        # Return elements that appear in at least 30% of lists
        element_counts = Counter(all_elements)
        threshold = len(lists) * 0.3
        
        return [element for element, count in element_counts.items() if count >= threshold]
    
    async def _update_rag_preferences(
        self, 
        user_id: str, 
        learned_preferences: Dict[str, Any]
    ):
        """Update RAG system with learned preferences"""
        try:
            # Store learned preferences in RAG context
            await self.rag_system.embed_and_store_newsletter(
                newsletter_id=f"preferences_{user_id}_{datetime.utcnow().isoformat()}",
                user_id=str(user_id),
                newsletter_data={
                    "type": "learned_preferences",
                    "content": f"User preferences learned from ratings: {learned_preferences}",
                    "preferences": learned_preferences,
                    "learned_at": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"Failed to update RAG preferences: {e}")


# Global service instance
rating_service = NewsletterRatingService()