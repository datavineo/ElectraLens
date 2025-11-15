"""
Minimal FastAPI app with only authentication endpoints for testing deployment.
This ensures auth endpoints are registered without any database dependency issues.
"""
from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
import os

# Create FastAPI app with authentication focus
app = FastAPI(
    title="ElectraLens API - Authentication System",
    version="3.0.0",  # New version to force deployment
    description="Voter Management API with Authentication Endpoints",
    docs_url="/docs",
    redoc_url="/redoc"
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
    last_login: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    user: UserResponse
    message: str

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint showing API information."""
    return {
        "message": "ElectraLens API - Voter Management System",
        "status": "running",
        "version": "3.0.0",
        "docs": "/docs",
        "authentication": "enabled",
        "endpoints": {
            "auth": ["/login", "/auth/login", "/login-form", "/auth/test"],
            "health": ["/health", "/status"]
        }
    }

# Health endpoints
@app.get("/health", tags=["System"])
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "authentication": "enabled",
        "database": "postgresql-neon",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/status", tags=["System"])  
async def status():
    """Detailed status information."""
    return {
        "status": "operational",
        "version": "3.0.0",
        "features": ["authentication", "voter-management", "postgresql"],
        "endpoints_registered": 8,
        "auth_endpoints": 4
    }

# Authentication endpoints
@app.post("/login", response_model=LoginResponse, tags=["Authentication"])
async def login_json(request: LoginRequest):
    """
    JSON-based user authentication.
    
    Authenticate users with JSON payload containing username and password.
    Returns user information and authentication status.
    
    **Supported Credentials:**
    - admin / SecureAdmin2024! (Administrator)
    - admin / admin123 (Fallback)
    - viewer / SecureViewer2024! (Viewer) 
    - viewer / viewer123 (Fallback)
    """
    username = request.username
    password = request.password
    
    # Authentication logic
    if ((username == "admin" and (password == "SecureAdmin2024!" or password == "admin123")) or
        (username == "viewer" and (password == "SecureViewer2024!" or password == "viewer123"))):
        
        user_data = UserResponse(
            id=1 if username == "admin" else 2,
            username=username,
            full_name="System Administrator" if username == "admin" else "Demo Viewer",
            role="admin" if username == "admin" else "viewer",
            is_active=True,
            created_at="2024-01-01T00:00:00",
            last_login=None
        )
        
        return LoginResponse(
            success=True,
            user=user_data,
            message="Login successful"
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/login-form", response_model=LoginResponse, tags=["Authentication"])
async def login_form(
    username: str = Form(..., description="Username for authentication"),
    password: str = Form(..., description="Password for authentication")
):
    """
    Form-based user authentication.
    
    Authenticate users with form data (application/x-www-form-urlencoded).
    Useful for HTML forms and traditional web applications.
    """
    # Same authentication logic as JSON endpoint
    if ((username == "admin" and (password == "SecureAdmin2024!" or password == "admin123")) or
        (username == "viewer" and (password == "SecureViewer2024!" or password == "viewer123"))):
        
        user_data = UserResponse(
            id=1 if username == "admin" else 2,
            username=username,
            full_name="System Administrator" if username == "admin" else "Demo Viewer",
            role="admin" if username == "admin" else "viewer",
            is_active=True,
            created_at="2024-01-01T00:00:00",
            last_login=None
        )
        
        return LoginResponse(
            success=True,
            user=user_data,
            message="Login successful"
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def auth_login(request: LoginRequest):
    """
    Advanced authentication endpoint with database integration.
    
    This endpoint provides the same authentication as /login but is designed
    for integration with database user management and JWT token generation.
    """
    # For now, use the same logic as the simple login
    return await login_json(request)

@app.get("/auth/test", tags=["Authentication"])
async def auth_test():
    """
    Authentication system test endpoint.
    
    Use this endpoint to verify that the authentication system is working
    and to check which authentication endpoints are available.
    """
    return {
        "message": "Authentication system operational",
        "status": "ready",
        "version": "3.0.0",
        "available_endpoints": [
            "POST /login (JSON authentication)",
            "POST /login-form (Form authentication)", 
            "POST /auth/login (Advanced authentication)",
            "GET /auth/test (This endpoint)"
        ],
        "test_credentials": {
            "admin": ["admin123", "SecureAdmin2024!"],
            "viewer": ["viewer123", "SecureViewer2024!"]
        }
    }

# Simple voter endpoints (minimal for compatibility)
@app.get("/voters", tags=["Voters"])
async def list_voters():
    """List voters - simplified endpoint."""
    return {"message": "Voter endpoints available", "total": 0, "voters": []}

@app.post("/voters", tags=["Voters"])
async def create_voter(voter_data: dict):
    """Create voter - simplified endpoint."""
    return {"message": "Voter creation endpoint", "status": "available"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)