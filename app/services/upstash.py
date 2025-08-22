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
    if redis_client is None and settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN:
        try:
            from upstash_redis import Redis

            redis_client = Redis(
                url=settings.UPSTASH_REDIS_REST_URL,
                token=settings.UPSTASH_REDIS_REST_TOKEN
            )
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
            from upstash_vector import Index

            vector_client = Index(
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
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        if not self.redis:
            return False
        try:
            self.redis.set(key, json.dumps(value), ex=ttl)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis:
            return False
        try:
            self.redis.delete(key)
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
            # Clean vector data to prevent serialization issues
            cleaned_vectors = []
            for vector_data in vectors:
                cleaned = {
                    "id": str(vector_data.get("id", "")),
                    "values": vector_data.get("values", []),
                    "metadata": {}
                }
                # Clean metadata
                metadata = vector_data.get("metadata", {})
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        cleaned["metadata"][key] = value
                    else:
                        # Convert complex objects to strings to avoid serialization issues
                        cleaned["metadata"][key] = str(value)
                
                cleaned_vectors.append(cleaned)
            
            await self.vector.upsert(cleaned_vectors)
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
            # Ensure vector is a list of floats
            if not isinstance(vector, list) or not all(isinstance(v, (int, float)) for v in vector):
                print(f"Vector query error: Invalid vector format: {type(vector)}")
                return []
            
            # Clean filter to avoid serialization issues
            clean_filter = {}
            if filter:
                for key, value in filter.items():
                    if isinstance(value, (str, int, float, bool)):
                        clean_filter[key] = value
                    else:
                        # Convert complex objects to strings
                        clean_filter[key] = str(value)
                
            result = self.vector.query(
                vector=vector, 
                top_k=top_k, 
                include_metadata=True, 
                filter=clean_filter
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
