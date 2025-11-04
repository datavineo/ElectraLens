from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db
import os
from typing import List

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='Voter Analysis API - Vercel')

# CORS middleware
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
        "message": "ElectraLens API", 
        "version": "1.0.0",
        "docs": "/docs",
        "voters": "/voters",
        "health": "/health"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "sqlite", "environment": "vercel"}

# Voter CRUD endpoints
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

# Bulk operations
@app.post("/voters/bulk")
async def create_voters_bulk(voters: List[schemas.VoterCreate], db: Session = Depends(get_db)):
    created_voters = []
    for voter in voters:
        try:
            created_voter = crud.create_voter(db=db, voter=voter)
            created_voters.append(created_voter)
        except Exception as e:
            continue
    return {"created": len(created_voters), "total": len(voters)}

# Search endpoint
@app.get("/voters/search/{name}")
async def search_voters(name: str, db: Session = Depends(get_db)):
    return crud.search_voters_by_name(db, name=name)

# Stats endpoint
@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_voters = crud.get_voter_count(db)
    return {
        "total_voters": total_voters,
        "database": "sqlite",
        "environment": "vercel"
    }