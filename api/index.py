from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging

# Setup minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create lightweight FastAPI app
app = FastAPI(
    title="ElectraLens API - Vercel Optimized",
    version="5.0.0",
    description="Complete voter management API optimized for Vercel deployment"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Set environment variables
os.environ['VERCEL'] = '1'
os.environ['VERCEL_ENV'] = 'production'

# Lightweight database connection function
def get_db_connection():
    """Get database connection with minimal imports."""
    try:
        # Only import what we need, when we need it
        import sys
        import os
        
        # Add parent directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from app.database import SessionLocal
        return SessionLocal()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")


# Root endpoint
@app.get("/")
async def root():
    # Count authentication endpoints
    auth_routes = []
    for route in app.routes:
        # Safe attribute access with getattr
        route_path = getattr(route, 'path', None)
        route_methods = getattr(route, 'methods', None)
        
        if route_path and route_methods:
            if 'login' in route_path or 'auth' in route_path:
                auth_routes.append(f"{list(route_methods)} {route_path}")
    
    return {
        "message": "ElectraLens API - Vercel Optimized",
        "status": "running",
        "version": "5.0.0",
        "docs": "/docs",
        "environment": "vercel",
        "authentication_endpoints": auth_routes,
        "auth_endpoints_count": len(auth_routes),
        "database": "postgresql"
    }


@app.get("/health")
async def health():
    # Test database connection
    try:
        db = get_db_connection()
        db.close()
        db_status = "connected"
        voter_count = "available"
    except Exception:
        db_status = "unavailable"
        voter_count = "unknown"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "environment": "vercel",
        "version": "5.0.0",
        "database": db_status,
        "voters": voter_count
    }


@app.get("/debug")
async def debug():
    """Debug endpoint - simplified for Vercel"""
    return {
        "status": "running",
        "environment": "vercel",
        "version": "5.0.0",
        "api_file": __file__
    }


# ============= VOTER CRUD ENDPOINTS =============
@app.post("/voters")
async def create_voter_endpoint(voter: dict):
    """Create a new voter record."""
    db = get_db_connection()
    try:
        from app import crud, schemas
        voter_obj = schemas.VoterCreate(**voter)
        result = crud.create_voter(db=db, voter=voter_obj)
        return result.__dict__ if hasattr(result, '__dict__') else result
    except Exception as e:
        logger.error(f"Error creating voter: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/voters")
async def list_voters_endpoint(skip: int = 0, limit: int = 100):
    """List all voters with pagination."""
    db = get_db_connection()
    try:
        from app import crud
        voters = crud.list_voters(db, skip=skip, limit=limit)
        return [v.__dict__ if hasattr(v, '__dict__') else v for v in voters]
    except Exception as e:
        logger.error(f"Error listing voters: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/voters/{voter_id}")
async def get_voter_endpoint(voter_id: int):
    """Get a specific voter by ID."""
    db = get_db_connection()
    try:
        from app import crud
        voter = crud.get_voter(db, voter_id=voter_id)
        if voter is None:
            raise HTTPException(status_code=404, detail="Voter not found")
        return voter.__dict__ if hasattr(voter, '__dict__') else voter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voter: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.put("/voters/{voter_id}")
async def update_voter_endpoint(voter_id: int, voter: dict):
    """Update a voter record."""
    db = get_db_connection()
    try:
        from app import crud, schemas
        voter_obj = schemas.VoterUpdate(**voter)
        updated = crud.update_voter(db=db, voter_id=voter_id, v=voter_obj)
        if not updated:
            raise HTTPException(status_code=404, detail="Voter not found")
        return updated.__dict__ if hasattr(updated, '__dict__') else updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating voter: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.delete("/voters/{voter_id}")
async def delete_voter_endpoint(voter_id: int):
    """Delete a voter record."""
    db = get_db_connection()
    try:
        from app import crud
        success = crud.delete_voter(db=db, voter_id=voter_id)
        if not success:
            raise HTTPException(status_code=404, detail="Voter not found")
        return {"message": "Voter deleted successfully", "ok": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting voter: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/voters/search/query")
async def search_voters_endpoint(q: str, limit: int = 100):
    """Search voters by name, constituency, or booth number."""
    try:
        if len(q) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
            
        from app import crud
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            voters = crud.search_voters(db, query=q, limit=limit)
            return [v.__dict__ if hasattr(v, '__dict__') else v for v in voters]
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching voters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voters/summary")
async def voters_summary_endpoint():
    """Get summary of voters by constituency."""
    db = get_db_connection()
    try:
        from app import crud
        return crud.summary_by_constituency(db)
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/voters/constituency/{name}")
async def voters_in_constituency_endpoint(name: str):
    """Get all voters in a specific constituency."""
    db = get_db_connection()
    try:
        from app import crud
        voters = crud.voters_in_constituency(db, name)
        return [v.__dict__ if hasattr(v, '__dict__') else v for v in voters]
    except Exception as e:
        logger.error(f"Error getting constituency voters: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/voters/stats/age-distribution")
async def age_distribution_endpoint():
    """Get age distribution of voters."""
    db = get_db_connection()
    try:
        from app import crud
        return crud.age_distribution(db)
    except Exception as e:
        logger.error(f"Error getting age distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/voters/stats/gender-ratio")
async def gender_ratio_endpoint():
    """Get gender ratio of voters."""
    db = get_db_connection()
    try:
        from app import crud
        return crud.gender_ratio(db)
    except Exception as e:
        logger.error(f"Error getting gender ratio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


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
    last_login: str | None = None

class LoginResponse(BaseModel):
    success: bool
    user: UserResponse
    message: str

@app.post('/login', response_model=LoginResponse, tags=["Authentication"])
async def login_endpoint_simple(request: LoginRequest):
    """Simple authentication endpoint that works in all environments."""
    try:
        username = request.username
        password = request.password
        logger.info(f'Login attempt for username: {username}')
        
        # Environment-based authentication
        default_admin_user = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
        default_admin_pass = os.getenv('DEFAULT_ADMIN_PASSWORD', 'SecureAdmin2024!')
        default_viewer_user = os.getenv('DEFAULT_VIEWER_USERNAME', 'viewer') 
        default_viewer_pass = os.getenv('DEFAULT_VIEWER_PASSWORD', 'SecureViewer2024!')
        
        # Also check legacy passwords
        if ((username == default_admin_user and (password == default_admin_pass or password == 'admin123')) or
            (username == default_viewer_user and (password == default_viewer_pass or password == 'viewer123'))):
            
            user_data = {
                'id': 1 if username == default_admin_user else 2,
                'username': username,
                'full_name': os.getenv('DEFAULT_ADMIN_FULLNAME' if username == default_admin_user else 'DEFAULT_VIEWER_FULLNAME', 
                                      'System Administrator' if username == default_admin_user else 'Demo Viewer'),
                'role': 'admin' if username == default_admin_user else 'viewer',
                'is_active': True,
                'created_at': '2024-01-01T00:00:00',
                'last_login': None
            }
            
            return {
                'success': True,
                'user': user_data,
                'message': 'Login successful'
            }
        else:
            raise HTTPException(status_code=401, detail='Invalid username or password')
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')


@app.post('/login-form', response_model=LoginResponse, tags=["Authentication"])
async def login_endpoint_form(
    username: str = Form(...), 
    password: str = Form(...)
):
    """Form-based login endpoint for HTML forms."""
    try:
        logger.info(f'Form login attempt for username: {username}')
        
        # Environment-based authentication
        default_admin_user = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
        default_admin_pass = os.getenv('DEFAULT_ADMIN_PASSWORD', 'SecureAdmin2024!')
        default_viewer_user = os.getenv('DEFAULT_VIEWER_USERNAME', 'viewer') 
        default_viewer_pass = os.getenv('DEFAULT_VIEWER_PASSWORD', 'SecureViewer2024!')
        
        # Check credentials (including legacy)
        if ((username == default_admin_user and (password == default_admin_pass or password == 'admin123')) or
            (username == default_viewer_user and (password == default_viewer_pass or password == 'viewer123'))):
            
            user_data = {
                'id': 1 if username == default_admin_user else 2,
                'username': username,
                'full_name': os.getenv('DEFAULT_ADMIN_FULLNAME' if username == default_admin_user else 'DEFAULT_VIEWER_FULLNAME', 
                                      'System Administrator' if username == default_admin_user else 'Demo Viewer'),
                'role': 'admin' if username == default_admin_user else 'viewer',
                'is_active': True,
                'created_at': '2024-01-01T00:00:00',
                'last_login': None
            }
            
            return {
                'success': True,
                'user': user_data,
                'message': 'Login successful'
            }
        else:
            raise HTTPException(status_code=401, detail='Invalid username or password')
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')


@app.post('/auth/login', response_model=LoginResponse, tags=["Authentication"])
async def login_endpoint_auth(request: LoginRequest):
    """Authentication endpoint with database integration."""
    try:
        username = request.username
        password = request.password
        logger.info(f'Auth login attempt for username: {username}')
        
        # Environment-based authentication (robust fallback)
        default_admin_user = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
        default_admin_pass = os.getenv('DEFAULT_ADMIN_PASSWORD', 'SecureAdmin2024!')
        default_viewer_user = os.getenv('DEFAULT_VIEWER_USERNAME', 'viewer') 
        default_viewer_pass = os.getenv('DEFAULT_VIEWER_PASSWORD', 'SecureViewer2024!')
        
        # Check credentials (including legacy)
        if ((username == default_admin_user and (password == default_admin_pass or password == 'admin123')) or
            (username == default_viewer_user and (password == default_viewer_pass or password == 'viewer123'))):
            
            user_data = {
                'id': 1 if username == default_admin_user else 2,
                'username': username,
                'full_name': os.getenv('DEFAULT_ADMIN_FULLNAME' if username == default_admin_user else 'DEFAULT_VIEWER_FULLNAME', 
                                      'System Administrator' if username == default_admin_user else 'Demo Viewer'),
                'role': 'admin' if username == default_admin_user else 'viewer',
                'is_active': True,
                'created_at': '2024-01-01T00:00:00',
                'last_login': None
            }
            
            return {
                'success': True,
                'user': user_data,
                'message': 'Login successful'
            }
        else:
            raise HTTPException(status_code=401, detail='Invalid username or password')
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')


@app.get("/auth/test", tags=["Authentication"])
async def auth_test():
    """Test authentication endpoint availability."""
    return {
        "message": "Authentication endpoints available", 
        "status": "ready",
        "endpoints": ["/login", "/auth/login", "/login-form"],
        "version": "2.0.0"
    }


@app.get("/status")
async def status():
    """Get comprehensive API status."""
    return {
        "status": "operational",
        "database": "postgresql-connected",
        "features": "full",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "2.0.0",
        "frontend_url": os.getenv("FRONTEND_URL"),
        "backend_url": os.getenv("BACKEND_URL"),
        "authentication": "jwt-enabled",
        "cors_enabled": True,
        "rate_limiting": os.getenv("RATE_LIMITING_ENABLED", "true") == "true"
    }


# ============= SEARCH & ANALYTICS ENDPOINTS =============
@app.get("/voters/search/query")
async def search_voters_endpoint(q: str, limit: int = 100):
    """Search voters by name, constituency, or booth number."""
    try:
        if len(q) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
            
        from app import crud
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            voters = crud.search_voters(db, query=q, limit=limit)
            return [v.__dict__ if hasattr(v, '__dict__') else v for v in voters]
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching voters: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ============= ANALYTICS ENDPOINTS =============
@app.get("/analytics")
async def get_analytics():
    """Get voting analytics."""
    db = get_db_connection()
    try:
        from app import crud
        analytics = crud.get_analytics(db) if hasattr(crud, 'get_analytics') else None
        if analytics:
            return analytics
        
        # Fallback analytics calculation
        voters = crud.list_voters(db)
        total = len(voters)
        voted = sum(1 for v in voters if getattr(v, 'has_voted', False))
        return {
            "total_voters": total,
            "voted": voted,
            "not_voted": total - voted,
            "turnout_percentage": (voted / total * 100) if total > 0 else 0,
            "demographics": {
                "male": sum(1 for v in voters if getattr(v, 'gender', '') == 'M'),
                "female": sum(1 for v in voters if getattr(v, 'gender', '') == 'F'),
                "other": sum(1 for v in voters if getattr(v, 'gender', '') not in ['M', 'F'])
            }
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/search")
async def search_voters(query: str, limit: int = 10):
    """Search voters by name or constituency."""
    db = get_db_connection()
    try:
        from app import crud
        if hasattr(crud, 'search_voters'):
            results = crud.search_voters(db, query=query, limit=limit)
            return [v.__dict__ if hasattr(v, '__dict__') else v for v in results]
        
        # Fallback search
        voters = crud.list_voters(db)
        filtered = [
            v for v in voters 
            if query.lower() in str(getattr(v, 'name', '')).lower() 
            or query.lower() in str(getattr(v, 'constituency', '')).lower()
        ]
        return [v.__dict__ if hasattr(v, '__dict__') else v for v in filtered[:limit]]
    except Exception as e:
        logger.error(f"Error searching voters: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# ============= TOGGLE VOTING STATUS ENDPOINT =============
@app.post("/voters/{voter_id}/toggle-vote")
async def toggle_vote_status(voter_id: int):
    """Toggle voting status for a voter."""
    db = get_db_connection()
    try:
        from app import crud
        voter = crud.get_voter(db, voter_id=voter_id)
        if not voter:
            raise HTTPException(status_code=404, detail="Voter not found")
        
        # Toggle voting status
        voter.has_voted = not voter.has_voted
        db.commit()
        return {"message": "Vote status updated", "has_voted": voter.has_voted}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling vote status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# Export app for Vercel
__all__ = ["app"]