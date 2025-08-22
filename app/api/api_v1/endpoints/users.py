from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_deps import get_current_user_from_token
from app.models.user import User
from app.utils.db_utils import db_utils
import uuid

router = APIRouter()


@router.get("/me")
async def get_current_user(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    try:
        return {
            "id": str(current_user.id),
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
            "profile_picture": getattr(current_user, 'profile_picture', None)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")


@router.put("/me")
async def update_current_user(
    user_data: dict,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        # Update user fields
        if user_data:
            for key, value in user_data.items():
                if hasattr(current_user, key) and key not in ['id', 'created_at']:
                    setattr(current_user, key, value)
        
        db.commit()
        return {"message": "User updated successfully", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
