from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, newsletters, preferences, users, email, agent_integration

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    newsletters.router, prefix="/newsletters", tags=["newsletters"]
)
api_router.include_router(
    preferences.router, prefix="/preferences", tags=["preferences"]
)
api_router.include_router(email.router, prefix="/email", tags=["email"])
api_router.include_router(
    agent_integration.router, prefix="/agents", tags=["agent-integration"]
)
