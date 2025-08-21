from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import secrets
import uuid
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import OTPRequest, OTPVerification, AuthResponse, SessionInfo
from app.services.email import email_service
from app.services.upstash import cache_service

router = APIRouter()

# Constants
OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 3
SESSION_EXPIRY_HOURS = 24

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

@router.post("/signup", response_model=AuthResponse)
async def signup(request: OTPRequest, db: Session = Depends(get_db)):
    """Send OTP for email signup"""
    try:
        email = request.email.lower().strip()
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        # Generate OTP
        otp_code = email_service.generate_otp()
        otp_expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        if existing_user:
            # Update existing user's OTP
            existing_user.otp_code = otp_code
            existing_user.otp_expires_at = otp_expires_at
            existing_user.otp_attempts = 0
            db.commit()
        else:
            # Create new user with OTP
            new_user = User(
                email=email,
                otp_code=otp_code,
                otp_expires_at=otp_expires_at,
                otp_attempts=0,
                is_active=False  # Will be activated after OTP verification
            )
            db.add(new_user)
            db.commit()
        
        # Send OTP email
        email_sent = await email_service.send_otp_email(email, otp_code)
        
        if not email_sent:
            # For development/testing, log the OTP
            print(f"🔐 OTP for {email}: {otp_code} (expires in {OTP_EXPIRY_MINUTES} minutes)")
            
        return AuthResponse(
            success=True,
            message=f"Verification code sent to {email}. Please check your email and enter the 6-digit code.",
            redirect_url=None
        )
        
    except Exception as e:
        print(f"❌ Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code. Please try again."
        )

@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: OTPVerification, db: Session = Depends(get_db)):
    """Verify OTP and create user session"""
    try:
        email = request.email.lower().strip()
        otp_code = request.otp_code
        
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please request a new verification code."
            )
        
        # Check if OTP exists and hasn't expired
        if not user.otp_code or not user.otp_expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verification code found. Please request a new one."
            )
        
        if datetime.utcnow() > user.otp_expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new one."
            )
        
        # Check attempt limit
        if user.otp_attempts >= MAX_OTP_ATTEMPTS:
            # Clear OTP to force new request
            user.otp_code = None
            user.otp_expires_at = None
            user.otp_attempts = 0
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Please request a new verification code."
            )
        
        # Verify OTP
        if user.otp_code != otp_code:
            user.otp_attempts += 1
            db.commit()
            remaining_attempts = MAX_OTP_ATTEMPTS - user.otp_attempts
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid verification code. {remaining_attempts} attempts remaining."
            )
        
        # OTP is valid - activate user and create session
        session_token = generate_session_token()
        user.is_active = True
        user.session_token = session_token
        user.last_login = datetime.utcnow()
        user.otp_code = None  # Clear OTP after successful verification
        user.otp_expires_at = None
        user.otp_attempts = 0
        db.commit()
        
        # Store session in cache
        session_data = {
            "user_id": str(user.id),
            "email": user.email,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)).isoformat()
        }
        await cache_service.set(
            f"session:{session_token}", 
            session_data, 
            ttl=SESSION_EXPIRY_HOURS * 3600
        )
        
        # Send welcome email for new users
        if not user.last_login or user.last_login == datetime.utcnow():
            await email_service.send_welcome_email(user.email, user.first_name)
        
        return AuthResponse(
            success=True,
            message="Email verified successfully! Welcome to Newsletter AI.",
            user_id=user.id,
            session_token=session_token,
            redirect_url="/dashboard"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ OTP verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed. Please try again."
        )

@router.post("/logout", response_model=AuthResponse)
async def logout(session_token: str = None):
    """Logout user and invalidate session"""
    try:
        if session_token:
            # Remove session from cache
            await cache_service.delete(f"session:{session_token}")
        
        return AuthResponse(
            success=True,
            message="Logged out successfully",
            redirect_url="/"
        )
        
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return AuthResponse(
            success=True,
            message="Logged out successfully",
            redirect_url="/"
        )

@router.get("/session", response_model=SessionInfo)
async def get_session(session_token: str, db: Session = Depends(get_db)):
    """Get current session information"""
    try:
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
        
        return SessionInfo(
            user_id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Session check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )