from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.post("/signup")
async def signup(email: str, db: Session = Depends(get_db)):
    """Send OTP for email signup"""
    # TODO: Implement OTP generation and email sending
    return {"message": "OTP sent to email", "email": email}

@router.post("/verify-otp")
async def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    """Verify OTP and create user session"""
    # TODO: Implement OTP verification and session creation
    return {"message": "OTP verified", "token": "placeholder-token"}

@router.post("/logout")
async def logout():
    """Logout user"""
    return {"message": "Logged out successfully"}