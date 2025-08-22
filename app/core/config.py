from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Newsletter AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Neon Database (PostgreSQL)
    DATABASE_URL: Optional[str] = None

    # Google Gemini API (primary LLM)
    GOOGLE_API_KEY: Optional[str] = None

    # OpenAI API (fallback and embeddings)
    OPENAI_API_KEY: Optional[str] = None

    # Portia AI
    PORTIA_API_KEY: Optional[str] = None

    # Upstash Redis
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None

    # Upstash Vector
    UPSTASH_VECTOR_URL: Optional[str] = None
    UPSTASH_VECTOR_TOKEN: Optional[str] = None

    # Email services
    RESEND_API_KEY: Optional[str] = None

    # Tavily API
    TAVILY_API_KEY: Optional[str] = None

    # CORS - using string to avoid JSON parsing issues
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8501"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list"""
        if not self.BACKEND_CORS_ORIGINS:
            return ["http://localhost:3000", "http://localhost:8501"]
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
