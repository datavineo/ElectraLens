from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import TYPE_CHECKING, List
import os
import sys
import logging
import traceback

# Type checking imports - these are always available for static analysis
if TYPE_CHECKING:
    from app import schemas, crud
    from app.database import get_db
    from sqlalchemy.orm import Session

# Setup logging first
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app first (before any imports that might fail)
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

# Try to import and setup everything with detailed error logging
initialization_error = None

try:
    # Set environment variables for Vercel
    os.environ['VERCEL'] = '1'
    os.environ['VERCEL_ENV'] = 'production'

    # Add parent directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    logger.info(f"Python path: {sys.path[:3]}")
    logger.info(f"Current dir: {current_dir}")
    
    # Import database components at runtime (also imported above for type checking)
    from app.database import get_db, Base, engine, SessionLocal  # type: ignore[misc]
    from app import models, schemas, crud  # type: ignore[misc]
    from sqlalchemy.orm import Session  # type: ignore[misc]
    
    logger.info("✓ All imports successful")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created")
    
    # Initialize sample data
    from app.init_data import init_sample_data
    init_sample_data()
    logger.info("✓ Sample data initialized")
    
    # Initialize admin users
    try:
        db = SessionLocal()
        admin_user = crud.get_user_by_username(db, "admin")
        if not admin_user:
            admin = crud.create_user(
                db=db,
                username="admin", 
                password="admin123",
                full_name="System Administrator",
                role="admin"
            )
            logger.info("✓ Default admin user created")
        else:
            logger.info("✓ Admin user already exists")
        db.close()
    except Exception as admin_error:
        logger.error(f"❌ Admin initialization failed: {admin_error}")
    
except Exception as e:
    initialization_error = {
        "error": str(e),
        "traceback": traceback.format_exc(),
        "type": type(e).__name__
    }
    logger.error(f"❌ Initialization failed: {e}")
    logger.error(f"Full traceback:\n{traceback.format_exc()}")


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ElectraLens API - Voter Management System",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "environment": "vercel",
        "initialization_status": "success" if initialization_error is None else "failed"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy" if initialization_error is None else "degraded",
        "environment": "vercel",
        "database": "sqlite-memory",
        "initialization_error": initialization_error
    }


@app.get("/debug")
async def debug():
    """Debug endpoint to see what's failing"""
    return {
        "python_version": sys.version,
        "sys_path": sys.path[:5],
        "environment_vars": {
            "VERCEL": os.getenv("VERCEL"),
            "VERCEL_ENV": os.getenv("VERCEL_ENV"),
        },
        "initialization_error": initialization_error,
        "cwd": os.getcwd(),
        "api_file": __file__
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