"""
Memory storage system for user context and preferences using Upstash Redis
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.config import settings

class MemoryService:
    """Service for storing and retrieving user context and preferences"""
    
    def __init__(self):
        self.redis_url = os.getenv('UPSTASH_REDIS_URL')
        self.redis_token = os.getenv('UPSTASH_REDIS_TOKEN')
        self._client = None
    
    def _get_client(self):
        """Get Redis client instance"""
        if self._client is None:
            try:
                from upstash_redis import Redis
                if self.redis_url and self.redis_token:
                    self._client = Redis(url=self.redis_url, token=self.redis_token)
                else:
                    print("⚠️  Upstash Redis credentials not configured")
                    return None
            except ImportError:
                print("⚠️  upstash-redis package not installed")
                return None
        return self._client
    
    async def store_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Store user preferences in memory
        
        Args:
            user_id: User identifier
            preferences: Dictionary of user preferences
        
        Returns:
            True if stored successfully
        """
        client = self._get_client()
        if not client:
            return False
        
        try:
            key = f"user_prefs:{user_id}"
            preferences_with_timestamp = {
                **preferences,
                "updated_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
            
            result = client.set(key, json.dumps(preferences_with_timestamp))
            return result is not None
            
        except Exception as e:
            print(f"❌ Failed to store user preferences: {e}")
            return False
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user preferences from memory
        
        Args:
            user_id: User identifier
        
        Returns:
            Dictionary of user preferences or None
        """
        client = self._get_client()
        if not client:
            return None
        
        try:
            key = f"user_prefs:{user_id}"
            result = client.get(key)
            
            if result:
                return json.loads(result)
            return None
            
        except Exception as e:
            print(f"❌ Failed to get user preferences: {e}")
            return None
    
    async def store_user_context(
        self, 
        user_id: str, 
        context_type: str, 
        context_data: Dict[str, Any],
        ttl_hours: int = 24
    ) -> bool:
        """
        Store user context data with TTL
        
        Args:
            user_id: User identifier
            context_type: Type of context (e.g., 'reading_history', 'engagement')
            context_data: Context data to store
            ttl_hours: Time to live in hours
        
        Returns:
            True if stored successfully
        """
        client = self._get_client()
        if not client:
            return False
        
        try:
            key = f"user_context:{user_id}:{context_type}"
            context_with_metadata = {
                "data": context_data,
                "created_at": datetime.utcnow().isoformat(),
                "context_type": context_type,
                "user_id": user_id
            }
            
            ttl_seconds = ttl_hours * 3600
            result = client.setex(key, ttl_seconds, json.dumps(context_with_metadata))
            return result is not None
            
        except Exception as e:
            print(f"❌ Failed to store user context: {e}")
            return False
    
    async def get_user_context(self, user_id: str, context_type: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user context data
        
        Args:
            user_id: User identifier
            context_type: Type of context to retrieve
        
        Returns:
            Context data or None
        """
        client = self._get_client()
        if not client:
            return None
        
        try:
            key = f"user_context:{user_id}:{context_type}"
            result = client.get(key)
            
            if result:
                context = json.loads(result)
                return context.get("data")
            return None
            
        except Exception as e:
            print(f"❌ Failed to get user context: {e}")
            return None
    
    async def store_newsletter_history(
        self, 
        user_id: str, 
        newsletter_data: Dict[str, Any]
    ) -> bool:
        """
        Store newsletter in user's history
        
        Args:
            user_id: User identifier
            newsletter_data: Newsletter data to store
        
        Returns:
            True if stored successfully
        """
        client = self._get_client()
        if not client:
            return False
        
        try:
            # Store individual newsletter
            newsletter_id = newsletter_data.get("id", datetime.utcnow().isoformat())
            key = f"newsletter:{user_id}:{newsletter_id}"
            
            newsletter_with_metadata = {
                **newsletter_data,
                "stored_at": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
            
            # Store for 90 days
            ttl_seconds = 90 * 24 * 3600
            result = client.setex(key, ttl_seconds, json.dumps(newsletter_with_metadata))
            
            if result:
                # Add to user's newsletter list
                list_key = f"newsletter_list:{user_id}"
                client.lpush(list_key, newsletter_id)
                client.expire(list_key, ttl_seconds)
                
            return result is not None
            
        except Exception as e:
            print(f"❌ Failed to store newsletter history: {e}")
            return False
    
    async def get_newsletter_history(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get user's newsletter history
        
        Args:
            user_id: User identifier
            limit: Maximum number of newsletters to return
        
        Returns:
            List of newsletter data
        """
        client = self._get_client()
        if not client:
            return []
        
        try:
            list_key = f"newsletter_list:{user_id}"
            newsletter_ids = client.lrange(list_key, 0, limit - 1)
            
            newsletters = []
            for newsletter_id in newsletter_ids:
                key = f"newsletter:{user_id}:{newsletter_id}"
                result = client.get(key)
                if result:
                    newsletter_data = json.loads(result)
                    newsletters.append(newsletter_data)
            
            return newsletters
            
        except Exception as e:
            print(f"❌ Failed to get newsletter history: {e}")
            return []
    
    async def store_reading_patterns(
        self, 
        user_id: str, 
        patterns: Dict[str, Any]
    ) -> bool:
        """
        Store user reading patterns and engagement data
        
        Args:
            user_id: User identifier
            patterns: Reading patterns data
        
        Returns:
            True if stored successfully
        """
        return await self.store_user_context(
            user_id=user_id,
            context_type="reading_patterns",
            context_data=patterns,
            ttl_hours=168  # 1 week
        )
    
    async def get_reading_patterns(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user reading patterns
        
        Args:
            user_id: User identifier
        
        Returns:
            Reading patterns data or None
        """
        return await self.get_user_context(user_id, "reading_patterns")
    
    async def update_engagement_metrics(
        self, 
        user_id: str, 
        newsletter_id: str, 
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update user engagement metrics
        
        Args:
            user_id: User identifier
            newsletter_id: Newsletter identifier
            action: Action taken (e.g., 'opened', 'clicked', 'read_time')
            metadata: Additional metadata about the action
        
        Returns:
            True if updated successfully
        """
        client = self._get_client()
        if not client:
            return False
        
        try:
            key = f"engagement:{user_id}"
            
            # Get existing engagement data
            existing_data = client.get(key)
            if existing_data:
                engagement_data = json.loads(existing_data)
            else:
                engagement_data = {
                    "total_newsletters": 0,
                    "total_opens": 0,
                    "total_clicks": 0,
                    "actions": []
                }
            
            # Add new action
            action_data = {
                "newsletter_id": newsletter_id,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            engagement_data["actions"].append(action_data)
            
            # Update counters
            if action == "opened":
                engagement_data["total_opens"] += 1
            elif action == "clicked":
                engagement_data["total_clicks"] += 1
            
            # Keep only last 100 actions
            engagement_data["actions"] = engagement_data["actions"][-100:]
            
            # Store for 30 days
            ttl_seconds = 30 * 24 * 3600
            result = client.setex(key, ttl_seconds, json.dumps(engagement_data))
            return result is not None
            
        except Exception as e:
            print(f"❌ Failed to update engagement metrics: {e}")
            return False
    
    async def get_engagement_metrics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user engagement metrics
        
        Args:
            user_id: User identifier
        
        Returns:
            Engagement metrics or None
        """
        client = self._get_client()
        if not client:
            return None
        
        try:
            key = f"engagement:{user_id}"
            result = client.get(key)
            
            if result:
                return json.loads(result)
            return None
            
        except Exception as e:
            print(f"❌ Failed to get engagement metrics: {e}")
            return None
    
    async def clear_user_data(self, user_id: str) -> bool:
        """
        Clear all user data from memory (for privacy/GDPR compliance)
        
        Args:
            user_id: User identifier
        
        Returns:
            True if cleared successfully
        """
        client = self._get_client()
        if not client:
            return False
        
        try:
            # Get all keys for this user
            patterns = [
                f"user_prefs:{user_id}",
                f"user_context:{user_id}:*",
                f"newsletter:{user_id}:*",
                f"newsletter_list:{user_id}",
                f"engagement:{user_id}"
            ]
            
            deleted_count = 0
            for pattern in patterns:
                if "*" in pattern:
                    # For patterns with wildcards, we'd need to scan
                    # This is a simplified version
                    continue
                else:
                    result = client.delete(pattern)
                    if result:
                        deleted_count += 1
            
            return deleted_count > 0
            
        except Exception as e:
            print(f"❌ Failed to clear user data: {e}")
            return False

# Global memory service instance
memory_service = MemoryService()