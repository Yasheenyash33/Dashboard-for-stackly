from sqlalchemy.orm import Session
from sqlalchemy import and_
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime

from . import models, schemas

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_users_by_role(db: Session, role: models.UserRole):
    return db.query(models.User).filter(models.User.role == role).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        is_temporary_password=user.is_temporary_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = pwd_context.hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.password_hash):
        return False
    return user

# Session CRUD operations
def get_session(db: Session, session_id: int):
    return db.query(models.Session).filter(models.Session.id == session_id).first()

def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Session).offset(skip).limit(limit).all()

def get_sessions_by_trainer(db: Session, trainer_id: int):
    return db.query(models.Session).filter(models.Session.trainer_id == trainer_id).all()

def get_sessions_by_trainee(db: Session, trainee_id: int):
    return db.query(models.Session).filter(models.Session.trainee_id == trainee_id).all()

def get_sessions_by_status(db: Session, status: models.SessionStatus):
    return db.query(models.Session).filter(models.Session.status == status).all()

def create_session(db: Session, session: schemas.SessionCreate):
    db_session = models.Session(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session(db: Session, session_id: int, session_update: schemas.SessionUpdate):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        return None

    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)

    db_session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_session)
    return db_session

def delete_session(db: Session, session_id: int):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False

# Analytics helper functions
def get_user_count_by_role(db: Session):
    from sqlalchemy import func
    result = db.query(models.User.role, func.count(models.User.id)).group_by(models.User.role).all()
    return {role.value: count for role, count in result}

def get_session_count_by_status(db: Session):
    from sqlalchemy import func
    result = db.query(models.Session.status, func.count(models.Session.id)).group_by(models.Session.status).all()
    return {status.value: count for status, count in result}
