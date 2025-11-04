from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'
os.environ['VERCEL_ENV'] = 'production'

# Create a basic working app first
app = FastAPI(title="ElectraLens API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "ElectraLens API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "environment": "vercel"}

# Try to import and add voter functionality
try:
    # Add parent directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    
    # Import database components
    from app.database import get_db, Base, engine
    from app import models, schemas, crud
    from sqlalchemy.orm import Session
    from typing import List
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize sample data
    def init_sample_data():
        db = next(get_db())
        try:
            # Check if data exists
            existing = crud.get_voters(db, skip=0, limit=1)
            if existing:
                return
            
            # Create sample voters
            sample_voters = [
                {"name": "John Doe", "age": 35, "address": "123 Main St", "phone": "555-0123", "email": "john@example.com", "vote": True},
                {"name": "Jane Smith", "age": 28, "address": "456 Oak Ave", "phone": "555-0456", "email": "jane@example.com", "vote": False},
                {"name": "Mike Johnson", "age": 42, "address": "789 Pine Rd", "phone": "555-0789", "email": "mike@example.com", "vote": True},
            ]
            
            for voter_data in sample_voters:
                voter = schemas.VoterCreate(**voter_data)
                crud.create_voter(db=db, voter=voter)
                
        finally:
            db.close()
    
    # Initialize data
    init_sample_data()
    
    # Add voter endpoints
    @app.get("/voters", response_model=List[schemas.Voter])
    async def get_voters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        return crud.get_voters(db, skip=skip, limit=limit)
    
    @app.post("/voters", response_model=schemas.Voter)
    async def create_voter(voter: schemas.VoterCreate, db: Session = Depends(get_db)):
        return crud.create_voter(db=db, voter=voter)
    
    @app.get("/voters/{voter_id}", response_model=schemas.Voter)
    async def get_voter(voter_id: int, db: Session = Depends(get_db)):
        db_voter = crud.get_voter(db, voter_id=voter_id)
        if db_voter is None:
            raise HTTPException(status_code=404, detail="Voter not found")
        return db_voter
    
    @app.put("/voters/{voter_id}", response_model=schemas.Voter)
    async def update_voter(voter_id: int, voter: schemas.VoterUpdate, db: Session = Depends(get_db)):
        return crud.update_voter(db=db, voter_id=voter_id, voter=voter)
    
    @app.delete("/voters/{voter_id}")
    async def delete_voter(voter_id: int, db: Session = Depends(get_db)):
        success = crud.delete_voter(db=db, voter_id=voter_id)
        if not success:
            raise HTTPException(status_code=404, detail="Voter not found")
        return {"message": "Voter deleted successfully"}
    
    @app.get("/voters/search/{name}")
    async def search_voters(name: str, db: Session = Depends(get_db)):
        return crud.search_voters_by_name(db, name=name)
    
    @app.get("/status")
    async def status():
        return {"status": "success", "database": "connected", "features": "full"}
        
except Exception as e:
    # Fallback endpoints if full functionality fails
    @app.get("/status")
    async def status_error():
        return {
            "status": "basic_mode",
            "error": str(e),
            "message": "Running with basic functionality only"
        }
    
    @app.get("/voters")
    async def voters_fallback():
        return [
            {"id": 1, "name": "Sample Voter", "age": 30, "vote": True},
            {"id": 2, "name": "Demo User", "age": 25, "vote": False}
        ]