from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'
os.environ['VERCEL_ENV'] = 'production'

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import database components
from app.database import get_db, Base, engine
from app import models, schemas, crud
from sqlalchemy.orm import Session
from typing import List
import logging

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ElectraLens API - Voter Management System",
    version="1.0.0",
    description="API for managing voter information"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

# Initialize sample data
try:
    from app.init_data import init_sample_data
    init_sample_data()
    logger.info("Sample data initialized")
except Exception as e:
    logger.warning(f"Could not initialize sample data: {e}")


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ElectraLens API - Voter Management System",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "environment": "vercel"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "environment": "vercel",
        "database": "sqlite-memory"
    }


# Voter CRUD endpoints
@app.post("/voters", response_model=schemas.VoterOut)
async def create_voter_endpoint(voter: schemas.VoterCreate, db: Session = Depends(get_db)):
    """Create a new voter record."""
    try:
        return crud.create_voter(db=db, voter=voter)
    except Exception as e:
        logger.error(f"Error creating voter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voters", response_model=List[schemas.VoterOut])
async def list_voters_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all voters with pagination."""
    try:
        return crud.list_voters(db, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error listing voters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voters/{voter_id}", response_model=schemas.VoterOut)
async def get_voter_endpoint(voter_id: int, db: Session = Depends(get_db)):
    """Get a specific voter by ID."""
    voter = crud.get_voter(db, voter_id=voter_id)
    if voter is None:
        raise HTTPException(status_code=404, detail="Voter not found")
    return voter


@app.put("/voters/{voter_id}", response_model=schemas.VoterOut)
async def update_voter_endpoint(voter_id: int, voter: schemas.VoterUpdate, db: Session = Depends(get_db)):
    """Update a voter record."""
    updated = crud.update_voter(db=db, voter_id=voter_id, v=voter)
    if not updated:
        raise HTTPException(status_code=404, detail="Voter not found")
    return updated


@app.delete("/voters/{voter_id}")
async def delete_voter_endpoint(voter_id: int, db: Session = Depends(get_db)):
    """Delete a voter record."""
    success = crud.delete_voter(db=db, voter_id=voter_id)
    if not success:
        raise HTTPException(status_code=404, detail="Voter not found")
    return {"message": "Voter deleted successfully", "ok": True}


@app.get("/voters/search/query", response_model=List[schemas.VoterOut])
async def search_voters_endpoint(q: str, limit: int = 100, db: Session = Depends(get_db)):
    """Search voters by name, constituency, or booth number."""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    return crud.search_voters(db, query=q, limit=limit)


@app.get("/voters/summary")
async def voters_summary_endpoint(db: Session = Depends(get_db)):
    """Get summary of voters by constituency."""
    return crud.summary_by_constituency(db)


@app.get("/voters/constituency/{name}", response_model=List[schemas.VoterOut])
async def voters_in_constituency_endpoint(name: str, db: Session = Depends(get_db)):
    """Get all voters in a specific constituency."""
    return crud.voters_in_constituency(db, name)


@app.get("/voters/stats/age-distribution")
async def age_distribution_endpoint(db: Session = Depends(get_db)):
    """Get age distribution of voters."""
    return crud.age_distribution(db)


@app.get("/voters/stats/gender-ratio")
async def gender_ratio_endpoint(db: Session = Depends(get_db)):
    """Get gender ratio of voters."""
    return crud.gender_ratio(db)


@app.get("/status")
async def status():
    """Get API status."""
    return {
        "status": "operational",
        "database": "connected",
        "features": "full",
        "environment": "vercel-serverless"
    }