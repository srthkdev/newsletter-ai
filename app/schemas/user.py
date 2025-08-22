from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None


class User(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(User):
    session_token: Optional[str] = None


# OTP Authentication Schemas
class OTPRequest(BaseModel):
    email: EmailStr

    @validator("email")
    def validate_email(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Email cannot be empty")
        return v.lower().strip()


class OTPVerification(BaseModel):
    email: EmailStr
    otp_code: str

    @validator("email")
    def validate_email(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Email cannot be empty")
        return v.lower().strip()

    @validator("otp_code")
    def validate_otp_code(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("OTP code cannot be empty")
        # Remove any spaces and ensure it's digits only
        cleaned = v.strip().replace(" ", "")
        if not cleaned.isdigit():
            raise ValueError("OTP code must contain only digits")
        if len(cleaned) != 6:
            raise ValueError("OTP code must be 6 digits")
        return cleaned


class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[uuid.UUID] = None
    session_token: Optional[str] = None
    redirect_url: Optional[str] = None


class SessionInfo(BaseModel):
    user_id: uuid.UUID
    email: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
