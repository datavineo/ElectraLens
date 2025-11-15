"""
Simple PostgreSQL authentication without bcrypt complexity.
"""
import hashlib
import secrets
from app.database import SessionLocal
from app import models
from sqlalchemy.orm import Session

def simple_hash_password(password: str) -> str:
    """Create a simple secure hash of the password."""
    # Use a combination of SHA-256 and a salt
    salt = "ElectraLens2024"  # Static salt for demo
    combined = f"{password}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()

def verify_simple_password(password: str, hashed: str) -> bool:
    """Verify password against simple hash."""
    return simple_hash_password(password) == hashed

def create_postgres_user(db: Session, username: str, password: str, full_name: str = "", role: str = "viewer"):
    """Create a user with simple password hashing."""
    
    # Check if user exists
    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        return existing
    
    # Create new user
    hashed_password = simple_hash_password(password)
    
    db_user = models.User(
        username=username,
        password_hash=hashed_password,
        full_name=full_name,
        role=role,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_postgres_user(db: Session, username: str, password: str):
    """Authenticate user with simple password verification."""
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    
    if not verify_simple_password(password, user.password_hash):
        return None
    
    if not user.is_active:
        return None
    
    return user

def init_postgres_users():
    """Initialize PostgreSQL users with simple authentication."""
    
    db = SessionLocal()
    try:
        # Create admin user
        admin = create_postgres_user(
            db=db,
            username="admin",
            password="admin123",
            full_name="System Administrator", 
            role="admin"
        )
        print(f"✅ Admin user: {admin.username}")
        
        # Create viewer user
        viewer = create_postgres_user(
            db=db,
            username="viewer",
            password="viewer123",
            full_name="Demo Viewer",
            role="viewer"
        )
        print(f"✅ Viewer user: {viewer.username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    init_postgres_users()