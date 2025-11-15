"""
Simple test to verify authentication endpoints are defined
"""
from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create minimal FastAPI app for testing
app = FastAPI(
    title="ElectraLens API - Voter Management System",
    version="2.0.0",
    description="API for managing voter information with authentication"
)

# Authentication models
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: str
    last_login: str | None = None

class LoginResponse(BaseModel):
    success: bool
    user: UserResponse
    message: str

# Authentication endpoints
@app.post('/login', response_model=LoginResponse, tags=["Authentication"])
async def login_endpoint_simple(request: LoginRequest):
    """Simple JSON-based authentication endpoint."""
    username = request.username
    password = request.password
    
    # Simple credential check
    if ((username == 'admin' and (password == 'SecureAdmin2024!' or password == 'admin123')) or
        (username == 'viewer' and (password == 'SecureViewer2024!' or password == 'viewer123'))):
        
        user_data = UserResponse(
            id=1 if username == 'admin' else 2,
            username=username,
            full_name='System Administrator' if username == 'admin' else 'Demo Viewer',
            role='admin' if username == 'admin' else 'viewer',
            is_active=True,
            created_at='2024-01-01T00:00:00',
            last_login=None
        )
        
        return LoginResponse(
            success=True,
            user=user_data,
            message='Login successful'
        )
    else:
        raise HTTPException(status_code=401, detail='Invalid username or password')

@app.post('/login-form', response_model=LoginResponse, tags=["Authentication"])
async def login_endpoint_form(username: str = Form(...), password: str = Form(...)):
    """Form-based authentication endpoint."""
    # Same logic as JSON endpoint
    if ((username == 'admin' and (password == 'SecureAdmin2024!' or password == 'admin123')) or
        (username == 'viewer' and (password == 'SecureViewer2024!' or password == 'viewer123'))):
        
        user_data = UserResponse(
            id=1 if username == 'admin' else 2,
            username=username,
            full_name='System Administrator' if username == 'admin' else 'Demo Viewer',
            role='admin' if username == 'admin' else 'viewer',
            is_active=True,
            created_at='2024-01-01T00:00:00',
            last_login=None
        )
        
        return LoginResponse(
            success=True,
            user=user_data,
            message='Login successful'
        )
    else:
        raise HTTPException(status_code=401, detail='Invalid username or password')

@app.post('/auth/login', response_model=LoginResponse, tags=["Authentication"])
async def login_endpoint_auth(request: LoginRequest):
    """Advanced authentication endpoint."""
    # Same logic as simple endpoint for now
    return await login_endpoint_simple(request)

@app.get("/auth/test", tags=["Authentication"])
async def auth_test():
    """Test authentication endpoint availability."""
    return {
        "message": "Authentication endpoints available", 
        "status": "ready",
        "endpoints": ["/login", "/auth/login", "/login-form"],
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "ElectraLens API - Authentication Test",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)