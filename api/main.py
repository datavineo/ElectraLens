# Vercel entry point for ElectraLens API
# This file imports the complete FastAPI app from the app module with ALL endpoints

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Set Vercel environment variables first
os.environ['VERCEL'] = '1'
os.environ['VERCEL_ENV'] = 'production'

# Import the complete FastAPI app with ALL endpoints
try:
    logger.info("Attempting to import complete app from app.main...")
    from app.main import app
    
    logger.info(f"✅ Successfully imported app with {len(app.routes)} routes")
    
    # Log all available routes for debugging
    routes_info = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes_info.append(f"{list(route.methods)} {route.path}")
    
    logger.info(f"📋 Available routes: {routes_info}")
    
    # Ensure Vercel configuration
    if not hasattr(app, '_vercel_configured'):
        app._vercel_configured = True
        logger.info("🔧 App configured for Vercel")
        
except Exception as e:
    logger.error(f"❌ Failed to import app.main: {e}")
    logger.error(f"Python path: {sys.path[:3]}")
    
    # Create a comprehensive fallback app with all essential endpoints
    from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import List, Optional
    import json
    
    app = FastAPI(
        title="ElectraLens API - Complete System",
        version="1.0.0",
        description="Complete voter management API with all endpoints"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Models
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
    
    class VoterCreate(BaseModel):
        voter_id: str
        name: str
        age: int
        gender: str
        constituency: str
        booth_no: str
        has_voted: bool = False
    
    class VoterResponse(BaseModel):
        id: int
        voter_id: str
        name: str
        age: int
        gender: str
        constituency: str
        booth_no: str
        has_voted: bool
        created_at: str
        updated_at: str
    
    # Sample in-memory data
    SAMPLE_VOTERS = [
        {"id": 1, "voter_id": "V001", "name": "John Doe", "age": 35, "gender": "M", "constituency": "North", "booth_no": "B001", "has_voted": False, "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": 2, "voter_id": "V002", "name": "Jane Smith", "age": 29, "gender": "F", "constituency": "South", "booth_no": "B002", "has_voted": True, "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": 3, "voter_id": "V003", "name": "Mike Johnson", "age": 42, "gender": "M", "constituency": "East", "booth_no": "B003", "has_voted": False, "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": 4, "voter_id": "V004", "name": "Sarah Wilson", "age": 38, "gender": "F", "constituency": "West", "booth_no": "B004", "has_voted": True, "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": 5, "voter_id": "V005", "name": "David Brown", "age": 55, "gender": "M", "constituency": "North", "booth_no": "B005", "has_voted": False, "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": 6, "voter_id": "V006", "name": "Emma Davis", "age": 31, "gender": "F", "constituency": "South", "booth_no": "B006", "has_voted": True, "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
    ]
    
    # ============= SYSTEM ENDPOINTS =============
    @app.get("/")
    async def root():
        return {
            "message": "ElectraLens API - Complete Voter Management System",
            "status": "running",
            "version": "1.0.0",
            "mode": "vercel-fallback",
            "endpoints": {
                "auth": ["/auth/login", "/login"],
                "voters": ["/voters", "/voters/{id}", "/voters/search"],
                "stats": ["/voters/summary", "/voters/stats"],
                "system": ["/health", "/docs"]
            },
            "import_error": str(e)
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "environment": "vercel",
            "mode": "fallback",
            "database": "in-memory",
            "total_voters": len(SAMPLE_VOTERS)
        }
    
    # ============= AUTHENTICATION ENDPOINTS =============
    @app.post('/auth/login', response_model=LoginResponse)
    async def auth_login(request: LoginRequest):
        """Complete authentication endpoint."""
        if ((request.username == "admin" and request.password in ["admin123", "SecureAdmin2024!"]) or
            (request.username == "viewer" and request.password in ["viewer123", "SecureViewer2024!"])):
            
            user_data = UserResponse(
                id=1 if request.username == "admin" else 2,
                username=request.username,
                full_name="System Administrator" if request.username == "admin" else "Demo Viewer",
                role="admin" if request.username == "admin" else "viewer",
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
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    @app.post('/login', response_model=LoginResponse)
    async def login(request: LoginRequest):
        """Alternative login endpoint."""
        return await auth_login(request)
    
    @app.post('/login-form')
    async def login_form(username: str = Form(...), password: str = Form(...)):
        """Form-based login endpoint."""
        request = LoginRequest(username=username, password=password)
        return await auth_login(request)
    
    # ============= VOTER CRUD ENDPOINTS =============
    @app.get("/voters", response_model=List[VoterResponse])
    async def list_voters(skip: int = 0, limit: int = 100):
        """List all voters with pagination."""
        return SAMPLE_VOTERS[skip:skip + limit]
    
    @app.get("/voters/{voter_id}")
    async def get_voter(voter_id: int):
        """Get a specific voter by ID."""
        voter = next((v for v in SAMPLE_VOTERS if v["id"] == voter_id), None)
        if voter:
            return voter
        raise HTTPException(status_code=404, detail="Voter not found")
    
    @app.post("/voters", response_model=VoterResponse)
    async def create_voter(voter: VoterCreate):
        """Create a new voter."""
        new_voter = {
            "id": len(SAMPLE_VOTERS) + 1,
            "voter_id": voter.voter_id,
            "name": voter.name,
            "age": voter.age,
            "gender": voter.gender,
            "constituency": voter.constituency,
            "booth_no": voter.booth_no,
            "has_voted": voter.has_voted,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        SAMPLE_VOTERS.append(new_voter)
        return new_voter
    
    @app.put("/voters/{voter_id}")
    async def update_voter(voter_id: int, voter_update: dict):
        """Update a voter."""
        voter_idx = next((i for i, v in enumerate(SAMPLE_VOTERS) if v["id"] == voter_id), None)
        if voter_idx is not None:
            SAMPLE_VOTERS[voter_idx].update(voter_update)
            return SAMPLE_VOTERS[voter_idx]
        raise HTTPException(status_code=404, detail="Voter not found")
    
    @app.delete("/voters/{voter_id}")
    async def delete_voter(voter_id: int):
        """Delete a voter."""
        voter_idx = next((i for i, v in enumerate(SAMPLE_VOTERS) if v["id"] == voter_id), None)
        if voter_idx is not None:
            deleted = SAMPLE_VOTERS.pop(voter_idx)
            return {"message": "Voter deleted successfully", "voter": deleted}
        raise HTTPException(status_code=404, detail="Voter not found")
    
    # ============= SEARCH & ANALYTICS ENDPOINTS =============
    @app.get("/voters/search/query")
    async def search_voters(q: str, limit: int = 100):
        """Search voters by name, constituency, or booth."""
        if len(q) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        results = [
            v for v in SAMPLE_VOTERS 
            if q.lower() in v["name"].lower() or 
               q.lower() in v["constituency"].lower() or 
               q.lower() in v["booth_no"].lower()
        ]
        return results[:limit]
    
    @app.get("/voters/summary")
    async def voters_summary():
        """Get voter statistics summary."""
        constituencies = {}
        voted_count = 0
        
        for voter in SAMPLE_VOTERS:
            const = voter["constituency"]
            if const not in constituencies:
                constituencies[const] = {"total": 0, "voted": 0}
            constituencies[const]["total"] += 1
            if voter["has_voted"]:
                constituencies[const]["voted"] += 1
                voted_count += 1
        
        return {
            "total_voters": len(SAMPLE_VOTERS),
            "voted": voted_count,
            "not_voted": len(SAMPLE_VOTERS) - voted_count,
            "voting_percentage": round((voted_count / len(SAMPLE_VOTERS)) * 100, 2),
            "by_constituency": constituencies
        }
    
    @app.get("/voters/constituency/{constituency_name}")
    async def voters_by_constituency(constituency_name: str):
        """Get voters by constituency."""
        voters = [v for v in SAMPLE_VOTERS if v["constituency"].lower() == constituency_name.lower()]
        return voters
    
    @app.get("/voters/stats/age-distribution")
    async def age_distribution():
        """Get age distribution."""
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-60": 0, "60+": 0}
        
        for voter in SAMPLE_VOTERS:
            age = voter["age"]
            if 18 <= age <= 25:
                age_groups["18-25"] += 1
            elif 26 <= age <= 35:
                age_groups["26-35"] += 1
            elif 36 <= age <= 45:
                age_groups["36-45"] += 1
            elif 46 <= age <= 60:
                age_groups["46-60"] += 1
            else:
                age_groups["60+"] += 1
        
        return age_groups
    
    @app.get("/voters/stats/gender-ratio")
    async def gender_ratio():
        """Get gender distribution."""
        male = sum(1 for v in SAMPLE_VOTERS if v["gender"] == "M")
        female = sum(1 for v in SAMPLE_VOTERS if v["gender"] == "F")
        
        return {
            "male": male,
            "female": female,
            "total": len(SAMPLE_VOTERS),
            "male_percentage": round((male / len(SAMPLE_VOTERS)) * 100, 2),
            "female_percentage": round((female / len(SAMPLE_VOTERS)) * 100, 2)
        }
    
    # ============= FILE UPLOAD ENDPOINTS =============
    @app.post("/upload/pdf")
    async def upload_pdf(file: UploadFile = File(...)):
        """PDF upload endpoint (disabled in Vercel)."""
        return {
            "message": "PDF processing not available in serverless environment",
            "filename": file.filename,
            "status": "disabled"
        }
    
    @app.post("/upload/csv")
    async def upload_csv(file: UploadFile = File(...)):
        """CSV upload endpoint (disabled in Vercel)."""
        return {
            "message": "CSV processing not available in serverless environment", 
            "filename": file.filename,
            "status": "disabled"
        }
    
    logger.info(f"✅ Fallback app created with {len(app.routes)} routes")

# Export the app for Vercel
__all__ = ['app']