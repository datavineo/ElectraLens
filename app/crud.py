from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Dict, Optional
from sqlalchemy import func
from .auth_config import AuthUtils, PasswordValidator
from datetime import datetime


def create_voter(db: Session, voter: schemas.VoterCreate):
    db_v = models.Voter(**voter.dict())
    db.add(db_v)
    db.commit()
    db.refresh(db_v)
    return db_v


def get_voter(db: Session, voter_id: int):
    return db.query(models.Voter).filter(models.Voter.id == voter_id).first()


def update_voter(db: Session, voter_id: int, v: schemas.VoterUpdate):
    db_v = get_voter(db, voter_id)
    if not db_v:
        return None
    for k, val in v.dict(exclude_unset=True).items():
        setattr(db_v, k, val)
    db.add(db_v)
    db.commit()
    db.refresh(db_v)
    return db_v


def delete_voter(db: Session, voter_id: int):
    db_v = get_voter(db, voter_id)
    if not db_v:
        return False
    db.delete(db_v)
    db.commit()
    return True


def list_voters(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Voter).offset(skip).limit(limit).all()


def count_voters(db: Session) -> int:
    """Count total number of voters in the database."""
    return db.query(models.Voter).count()


def summary_by_constituency(db: Session) -> List[Dict]:
    q = db.query(models.Voter.constituency, func.count(models.Voter.id)).group_by(models.Voter.constituency).all()
    return [{'constituency': c or 'UNKNOWN', 'count': cnt} for c, cnt in q]


def voters_in_constituency(db: Session, name: str):
    return db.query(models.Voter).filter(models.Voter.constituency == name).all()


def age_distribution(db: Session):
    """Get age distribution in bins using single efficient query."""
    from sqlalchemy import case
    
    # Single query with CASE/WHEN for efficiency
    result = db.query(
        case(
            (models.Voter.age < 18, '0-17'),
            (models.Voter.age <= 30, '18-30'),
            (models.Voter.age <= 45, '31-45'),
            (models.Voter.age <= 60, '46-60'),
            else_='61+'
        ).label('age_range'),
        func.count(models.Voter.id).label('count')
    ).filter(models.Voter.age != None).group_by('age_range').all()
    
    # Initialize all bins
    bins = {'0-17': 0, '18-30': 0, '31-45': 0, '46-60': 0, '61+': 0}
    
    # Populate from query results
    for age_range, count in result:
        bins[age_range] = count
    
    return bins


def gender_ratio(db: Session):
    q = db.query(models.Voter.gender, func.count(models.Voter.id)).group_by(models.Voter.gender).all()
    return {g or 'UNKNOWN': cnt for g, cnt in q}


def search_voters(db: Session, query: str, limit: int = 100):
    """Search voters by name or constituency (case-insensitive)."""
    search_term = f'%{query}%'
    return db.query(models.Voter).filter(
        (models.Voter.name.ilike(search_term)) | 
        (models.Voter.constituency.ilike(search_term)) |
        (models.Voter.booth_no.ilike(search_term))
    ).limit(limit).all()


def filter_by_constituency(db: Session, constituency: str, limit: int = 100):
    """Get voters by exact constituency match."""
    return db.query(models.Voter).filter(
        models.Voter.constituency == constituency
    ).limit(limit).all()


def filter_by_gender(db: Session, gender: str, limit: int = 100):
    """Get voters by exact gender match."""
    return db.query(models.Voter).filter(
        models.Voter.gender == gender
    ).limit(limit).all()


def filter_by_age_range(db: Session, min_age: int, max_age: int, limit: int = 100):
    """Get voters within age range."""
    return db.query(models.Voter).filter(
        models.Voter.age >= min_age,
        models.Voter.age <= max_age
    ).limit(limit).all()


# ============= USER AUTHENTICATION FUNCTIONS =============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return AuthUtils.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    return AuthUtils.get_password_hash(password)


def create_user(db: Session, username: str, password: str, full_name: str = "", role: str = "viewer"):
    """Create a new user with hashed password."""
    # Validate password strength
    is_valid, message = PasswordValidator.validate_password(password)
    if not is_valid:
        raise ValueError(f"Password validation failed: {message}")
    
    # Check if user already exists
    existing_user = get_user_by_username(db, username)
    if existing_user:
        raise ValueError(f"User with username '{username}' already exists")
    
    # Validate role
    if role not in ["admin", "viewer"]:
        raise ValueError(f"Invalid role '{role}'. Must be 'admin' or 'viewer'")
    
    hashed_password = get_password_hash(password)
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


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Authenticate user with username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):  # type: ignore
        return None
    if not user.is_active:  # type: ignore
        return None
    
    # Update last login time
    user.last_login = datetime.utcnow()  # type: ignore
    db.commit()
    
    return user


def list_users(db: Session, skip: int = 0, limit: int = 100):
    """List all users."""
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, full_name: Optional[str] = None, role: Optional[str] = None, is_active: Optional[bool] = None):
    """Update user details."""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    if full_name is not None:
        user.full_name = full_name  # type: ignore
    if role is not None:
        user.role = role  # type: ignore
    if is_active is not None:
        user.is_active = is_active  # type: ignore
    
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user_id: int, new_password: str):
    """Change user password."""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.password_hash = get_password_hash(new_password)  # type: ignore
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
