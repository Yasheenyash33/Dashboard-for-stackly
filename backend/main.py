from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import jwt
import json
import io
from datetime import datetime, timedelta
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import models, schemas, crud, reporting
from backend.database import engine, get_db, SessionLocal

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Training Management API", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# Authentication functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Authentication routes
@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "force_password_change": user.is_temporary_password
    }

# User routes
@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ["admin", "trainer"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ["admin", "trainer"] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")

    # Check if username or email already exists
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    created_user = crud.create_user(db, user)

    # Broadcast user creation event
    await manager.broadcast({
        "type": "user_created",
        "data": {
            "user_id": created_user.id,
            "action": "created",
            "user": created_user.__dict__
        }
    })

    return created_user

@app.put("/users/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    updated_user = crud.update_user(db, user_id, user_update)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Broadcast user update event
    await manager.broadcast({
        "type": "user_updated",
        "data": {
            "user_id": user_id,
            "action": "updated",
            "user": updated_user.__dict__
        }
    })

    return updated_user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")

    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    # Broadcast user deletion event
    await manager.broadcast({
        "type": "user_deleted",
        "data": {
            "user_id": user_id,
            "action": "deleted"
        }
    })

    return {"message": "User deleted successfully"}

# Session routes
@app.get("/sessions/", response_model=List[schemas.Session])
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sessions = crud.get_sessions(db, skip=skip, limit=limit)
    return sessions

@app.get("/sessions/{session_id}", response_model=schemas.Session)
def read_session(session_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    session = crud.get_session(db, session_id=session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.post("/sessions/", response_model=schemas.Session)
async def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ["admin", "trainer"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    created_session = crud.create_session(db, session)

    # Broadcast session creation event
    await manager.broadcast({
        "type": "session_created",
        "data": {
            "session_id": created_session.id,
            "status": created_session.status.value,
            "updated_at": created_session.updated_at.isoformat()
        }
    })

    return created_session

@app.put("/sessions/{session_id}", response_model=schemas.Session)
async def update_session(session_id: int, session_update: schemas.SessionUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ["admin", "trainer"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    updated_session = crud.update_session(db, session_id, session_update)
    if updated_session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Broadcast session update event
    await manager.broadcast({
        "type": "session_updated",
        "data": {
            "session_id": session_id,
            "status": updated_session.status.value,
            "updated_at": updated_session.updated_at.isoformat()
        }
    })

    return updated_session

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete sessions")

    success = crud.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    # Broadcast session deletion event
    await manager.broadcast({
        "type": "session_deleted",
        "data": {
            "session_id": session_id
        }
    })

    return {"message": "Session deleted successfully"}

# Analytics routes
@app.get("/analytics/users")
def get_user_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_user_count_by_role(db)

@app.get("/analytics/sessions")
def get_session_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_session_count_by_status(db)

# Report generation endpoint
@app.get("/reports/generate")
def generate_report(format: str = "pdf", db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    users = crud.get_users(db)
    sessions = crud.get_sessions(db)

    if format == "csv":
        report_data = reporting.generate_csv_report(users, sessions)
        return StreamingResponse(
            io.StringIO(report_data.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=training-report-{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    elif format == "excel":
        report_data = reporting.generate_excel_report(users, sessions)
        return StreamingResponse(
            report_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=training-report-{datetime.now().strftime('%Y%m%d')}.xlsx"}
        )
    elif format == "pdf":
        report_data = reporting.generate_pdf_report(users, sessions)
        return StreamingResponse(
            report_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=training-report-{datetime.now().strftime('%Y%m%d')}.pdf"}
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'pdf', 'excel', or 'csv'")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for testing, or handle client messages
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Training Management API", "docs": "/docs", "health": "/health"}

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
