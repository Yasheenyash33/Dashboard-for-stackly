from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    trainer = "trainer"
    trainee = "trainee"

class SessionStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str
    is_temporary_password: bool = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_temporary_password: Optional[bool] = None

class User(UserBase):
    id: int
    is_temporary_password: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Session schemas
class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    trainer_id: int
    trainee_id: int
    scheduled_date: datetime
    duration_minutes: int
    status: SessionStatus = SessionStatus.scheduled

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    trainer_id: Optional[int] = None
    trainee_id: Optional[int] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[SessionStatus] = None

class Session(SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Authentication schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
    force_password_change: bool = False

# Real-time update schemas
class SessionUpdateEvent(BaseModel):
    session_id: int
    status: SessionStatus
    updated_at: datetime

class UserUpdateEvent(BaseModel):
    user_id: int
    action: str  # "created", "updated", "deleted"
    user: Optional[User] = None
