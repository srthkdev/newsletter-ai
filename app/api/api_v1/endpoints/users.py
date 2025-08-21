from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.get("/me")
async def get_current_user(db: Session = Depends(get_db)):
    """Get current user information"""
    # TODO: Implement user retrieval
    return {"message": "Current user endpoint"}

@router.put("/me")
async def update_current_user(db: Session = Depends(get_db)):
    """Update current user information"""
    # TODO: Implement user update
    return {"message": "User updated"}