"""
Embedding service for RAG functionality using OpenAI embeddings
"""
from typing import List, Dict, Any, Optional
import openai
from app.core.config import settings
from app.services.upstash import vector_service
import uuid
import hashlib

class EmbeddingService:
    """Service for creating and managing embeddings"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        self.model = "text-embedding-3-small"  # Cost-effective embedding model
    
    async def create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding for text using OpenAI"""
        try:
            response = await openai.embeddings.acreate(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding creation error: {e}")
            return None
    
    async def embed_newsletter(self, newsletter_id: str, user_id: str, 
                              content: str, metadata: Dict[str, Any]) -> bool:
        """Embed newsletter content for RAG retrieval"""
        try:
            # Create embedding
            embedding = await self.create_embedding(content)
            if not embedding:
                return False
            
            # Create unique ID for the vector
            vector_id = f"newsletter_{newsletter_id}_{user_id}"
            
            # Prepare vector data
            vector_data = {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "newsletter_id": newsletter_id,
                    "user_id": user_id,
                    "content_hash": hashlib.md5(content.encode()).hexdigest(),
                    "type": "newsletter",
                    **metadata
                }
            }
            
            # Store in vector database
            return await vector_service.upsert([vector_data])
        
        except Exception as e:
            print(f"Newsletter embedding error: {e}")
            return False
    
    async def search_similar_content(self, query: str, user_id: str, 
                                   top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content in user's newsletter history"""
        try:
            # Create query embedding
            query_embedding = await self.create_embedding(query)
            if not query_embedding:
                return []
            
            # Search with user filter
            filter_criteria = {"user_id": user_id, "type": "newsletter"}
            
            results = await vector_service.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_criteria
            )
            
            return [
                {
                    "newsletter_id": match.metadata.get("newsletter_id"),
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results
            ]
        
        except Exception as e:
            print(f"Content search error: {e}")
            return []
    
    async def get_user_content_suggestions(self, user_id: str, 
                                         topics: List[str]) -> List[str]:
        """Get personalized content suggestions based on user history"""
        try:
            suggestions = []
            
            for topic in topics:
                similar_content = await self.search_similar_content(
                    query=f"newsletter about {topic}",
                    user_id=user_id,
                    top_k=3
                )
                
                if similar_content:
                    suggestions.extend([
                        f"More content about {topic} based on your reading history",
                        f"Deep dive into {topic} trends you've shown interest in"
                    ])
            
            return suggestions[:5]  # Limit to 5 suggestions
        
        except Exception as e:
            print(f"Content suggestions error: {e}")
            return []

# Global embedding service instance
embedding_service = EmbeddingService()