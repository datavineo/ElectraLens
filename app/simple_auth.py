"""
Simple authentication system without JWT for local development.
"""
from app.database import SessionLocal
from app import models
from sqlalchemy.orm import Session

def init_simple_auth():
    """Initialize simple authentication with hardcoded users for demo."""
    # For now, let's create a simple working authentication
    return True

# Simple user validation function
def validate_user(username: str, password: str):
    """Simple user validation for local development."""
    # Hardcoded credentials for demo
    users = {
        "admin": {"password": "admin123", "role": "admin", "full_name": "Administrator"},
        "viewer": {"password": "viewer123", "role": "viewer", "full_name": "Viewer"}
    }
    
    if username in users and users[username]["password"] == password:
        return {
            "id": 1 if username == "admin" else 2,
            "username": username,
            "role": users[username]["role"],
            "full_name": users[username]["full_name"],
            "is_active": True
        }
    return None