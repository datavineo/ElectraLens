from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Dict
from sqlalchemy import func


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
