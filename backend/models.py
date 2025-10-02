from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from .database import Base

class UserRole(PyEnum):
    admin = "admin"
    trainer = "trainer"
    trainee = "trainee"

class SessionStatus(PyEnum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    is_temporary_password = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions_as_trainer = relationship("Session", back_populates="trainer", foreign_keys="Session.trainer_id")
    sessions_as_trainee = relationship("Session", back_populates="trainee", foreign_keys="Session.trainee_id")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trainee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.scheduled)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trainer = relationship("User", back_populates="sessions_as_trainer", foreign_keys=[trainer_id])
    trainee = relationship("User", back_populates="sessions_as_trainee", foreign_keys=[trainee_id])
