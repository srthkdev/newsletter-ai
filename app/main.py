from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import create_tables
from app.api.api_v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Newsletter AI...")

    # Initialize database tables
    try:
        create_tables()
        print("✅ Database tables initialized")
    except Exception as e:
        print(f"⚠️  Database initialization: {e}")
        print("   This is expected if using cloud database without connection")

    # Test cloud services
    from app.services.upstash import get_redis_client, get_vector_client

    redis = get_redis_client()
    if redis:
        print("✅ Upstash Redis connected")
    else:
        print("⚠️  Upstash Redis not configured (expected without env vars)")

    vector = get_vector_client()
    if vector:
        print("✅ Upstash Vector connected")
    else:
        print("⚠️  Upstash Vector not configured (expected without env vars)")

    # Test Portia AI
    from app.portia.config import get_portia_client

    portia = get_portia_client()
    if portia:
        print("✅ Portia AI client initialized")
    else:
        print("⚠️  Portia AI not configured (expected without API keys)")

    yield

    # Shutdown
    print("👋 Shutting down Newsletter AI...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Newsletter AI - Intelligent newsletter creation and distribution platform using Portia AI, Neon DB, and Upstash",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Newsletter AI API",
        "version": settings.VERSION,
        "description": "Intelligent newsletter platform with Portia AI agents",
        "services": {
            "database": "Neon PostgreSQL",
            "cache": "Upstash Redis",
            "vector": "Upstash Vector",
            "ai": "Portia AI + OpenAI",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.services.upstash import get_redis_client, get_vector_client

    services = {
        "api": "healthy",
        "database": "unknown",
        "redis": "disconnected",
        "vector": "disconnected",
    }

    # Check Redis
    redis = get_redis_client()
    if redis:
        try:
            await redis.ping()
            services["redis"] = "connected"
        except:
            services["redis"] = "error"

    # Check Vector
    vector = get_vector_client()
    if vector:
        services["vector"] = "configured"

    return {"status": "healthy", "services": services}
