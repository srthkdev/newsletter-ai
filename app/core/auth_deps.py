"""
Authentication dependencies for FastAPI endpoints
"""
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.core.database import get_db
from app.models.user import User
from app.services.upstash import cache_service


async def get_current_user_from_token(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract current user from Authorization header containing session token
    Expected format: "Bearer <session_token>"
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        # Parse Bearer token
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        session_token = authorization[7:]  # Remove "Bearer " prefix
        
        # Check session in cache
        session_data = await cache_service.get(f"session:{session_token}")
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
        
        # Get user from database
        user_id = uuid.UUID(session_data["user_id"])
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in session"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Extract current user from Authorization header, but don't raise if missing
    Returns None if no valid authentication is provided
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user_from_token(authorization, db)
    except HTTPException:
        return None


def get_current_user_id(current_user: User = Depends(get_current_user_from_token)) -> str:
    """
    Simple dependency to get just the user ID string
    """
    return str(current_user.id)


def get_current_user_id_optional(current_user: Optional[User] = Depends(get_current_user_optional)) -> Optional[str]:
    """
    Simple dependency to get just the user ID string, optional
    """
    return str(current_user.id) if current_user else None