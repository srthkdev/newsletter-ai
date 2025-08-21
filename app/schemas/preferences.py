from pydantic import BaseModel
from typing import List, Optional
import uuid

class PreferencesBase(BaseModel):
    topics: List[str] = []
    tone: str = "professional"
    frequency: str = "weekly"
    custom_instructions: Optional[str] = None
    preferred_length: str = "medium"

class PreferencesCreate(PreferencesBase):
    user_id: uuid.UUID

class PreferencesUpdate(BaseModel):
    topics: Optional[List[str]] = None
    tone: Optional[str] = None
    frequency: Optional[str] = None
    custom_instructions: Optional[str] = None
    preferred_length: Optional[str] = None

class Preferences(PreferencesBase):
    id: uuid.UUID
    user_id: uuid.UUID
    
    class Config:
        orm_mode = True