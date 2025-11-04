from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import sys
from typing import List

# Set environment variables for Vercel
os.environ.setdefault('VERCEL', '1')
os.environ.setdefault('VERCEL_ENV', 'production')

# Add parent directory to Python path for app imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  
sys.path.insert(0, parent_dir)

# Create the main FastAPI app
app = FastAPI(
    title="ElectraLens API", 
    version="1.0.0",
    description="Voter Management System API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic endpoints
@app.get("/")
async def root():
    return {
        "message": "ElectraLens API is running on Vercel",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": "ElectraLens",
        "environment": "vercel"
    }

# Try to import the Vercel-compatible main app
try:
    from app.main_vercel import app as vercel_app
    
    # Mount the vercel app
    app.mount("/api", vercel_app)
    
    @app.get("/api/status")
    async def api_status():
        return {
            "status": "success",
            "app": "vercel_compatible",
            "database": "sqlite"
        }
        
except Exception as e:
    # Fallback: Try to set up database and routes manually
    try:
        from app.database import get_db, Base, engine
        from app import models, schemas, crud
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Voter endpoints
        @app.get("/api/voters", response_model=List[schemas.Voter])
        async def get_voters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            return crud.get_voters(db, skip=skip, limit=limit)
        
        @app.post("/api/voters", response_model=schemas.Voter)
        async def create_voter(voter: schemas.VoterCreate, db: Session = Depends(get_db)):
            return crud.create_voter(db=db, voter=voter)
        
        @app.get("/api/voters/{voter_id}", response_model=schemas.Voter)
        async def get_voter(voter_id: int, db: Session = Depends(get_db)):
            db_voter = crud.get_voter(db, voter_id=voter_id)
            if db_voter is None:
                raise HTTPException(status_code=404, detail="Voter not found")
            return db_voter
        
        @app.put("/api/voters/{voter_id}", response_model=schemas.Voter)
        async def update_voter(voter_id: int, voter: schemas.VoterUpdate, db: Session = Depends(get_db)):
            return crud.update_voter(db=db, voter_id=voter_id, voter=voter)
        
        @app.delete("/api/voters/{voter_id}")
        async def delete_voter(voter_id: int, db: Session = Depends(get_db)):
            success = crud.delete_voter(db=db, voter_id=voter_id)
            if not success:
                raise HTTPException(status_code=404, detail="Voter not found")
            return {"message": "Voter deleted successfully"}
        
        @app.get("/api/status")
        async def api_status_manual():
            return {
                "status": "success",
                "mode": "manual_setup",
                "database": "sqlite"
            }
            
    except Exception as e2:
        @app.get("/api/status")
        async def api_status_error():
            return {
                "status": "error",
                "error": str(e2),
                "original_error": str(e),
                "message": "All imports failed - running in minimal mode"
            }
        
        @app.get("/api/voters")
        async def get_voters_fallback():
            return []