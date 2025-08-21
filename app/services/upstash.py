"""
Upstash services for Redis caching and Vector storage
"""

from typing import List, Dict, Any, Optional
import json
from app.core.config import settings

# Redis client for caching and sessions
redis_client = None
vector_client = None


def get_redis_client():
    """Get Upstash Redis client"""
    global redis_client
    if redis_client is None and settings.UPSTASH_REDIS_URL:
        try:
            from upstash_redis import Redis

            redis_client = Redis.from_env()
        except ImportError:
            print(
                "upstash-redis not installed. Install with: pip install upstash-redis"
            )
        except Exception as e:
            print(f"Failed to initialize Upstash Redis: {e}")
    return redis_client


def get_vector_client():
    """Get Upstash Vector client"""
    global vector_client
    if vector_client is None and settings.UPSTASH_VECTOR_URL:
        try:
            from upstash_vector import Vector

            vector_client = Vector(
                url=settings.UPSTASH_VECTOR_URL, token=settings.UPSTASH_VECTOR_TOKEN
            )
        except ImportError:
            print(
                "upstash-vector not installed. Install with: pip install upstash-vector"
            )
        except Exception as e:
            print(f"Failed to initialize Upstash Vector: {e}")
    return vector_client


class CacheService:
    """Redis-based caching service"""

    def __init__(self):
        self.redis = get_redis_client()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        if not self.redis:
            return False
        try:
            await self.redis.set(key, json.dumps(value), ex=ttl)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis:
            return False
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False


class VectorService:
    """Vector storage service for RAG"""

    def __init__(self):
        self.vector = get_vector_client()

    async def upsert(self, vectors: List[Dict[str, Any]]) -> bool:
        """Store vectors in Upstash Vector"""
        if not self.vector:
            return False
        try:
            await self.vector.upsert(vectors)
            return True
        except Exception as e:
            print(f"Vector upsert error: {e}")
            return False

    async def query(
        self, vector: List[float], top_k: int = 5, filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Query similar vectors"""
        if not self.vector:
            return []
        try:
            result = await self.vector.query(
                vector=vector, top_k=top_k, include_metadata=True, filter=filter
            )
            return result.matches if result else []
        except Exception as e:
            print(f"Vector query error: {e}")
            return []

    async def delete(self, ids: List[str]) -> bool:
        """Delete vectors by IDs"""
        if not self.vector:
            return False
        try:
            await self.vector.delete(ids)
            return True
        except Exception as e:
            print(f"Vector delete error: {e}")
            return False


# Global service instances
cache_service = CacheService()
vector_service = VectorService()
