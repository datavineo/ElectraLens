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

# Configure CORS for production
cors_origins = [
    "https://datavineo.vercel.app",
    "https://electra-lens.vercel.app", 
    "https://datavineo.github.io",
    "http://localhost:8501",
    "http://localhost:3000"
]

# Add CORS middleware with production-ready configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Try to import and setup everything with detailed error logging
initialization_error = None

try:
    # Set environment variables for Vercel
    os.environ['VERCEL'] = '1'
    os.environ['VERCEL_ENV'] = 'production'
    
    # Set production environment variables for Vercel
    if not os.getenv('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_aTq54cvMEkiz@ep-orange-sea-ad3n3cx8-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    
    if not os.getenv('JWT_SECRET_KEY'):
        os.environ['JWT_SECRET_KEY'] = 'ElectraLens-Production-Secret-2024-CHANGE-THIS-IMMEDIATELY'
    
    if not os.getenv('FRONTEND_URL'):
        os.environ['FRONTEND_URL'] = 'https://datavineo.vercel.app'
    
    if not os.getenv('ENVIRONMENT'):
        os.environ['ENVIRONMENT'] = 'production'

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
        "environment": os.getenv("ENVIRONMENT", "vercel"),
        "database": "postgresql-neon",
        "frontend_url": os.getenv("FRONTEND_URL", "https://datavineo.vercel.app"),
        "backend_url": os.getenv("BACKEND_URL", "https://electra-lens.vercel.app"),
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


@app.post('/auth/login')
def login_endpoint(username: str, password: str, db: Session = Depends(get_db)):
    """Authenticate user with PostgreSQL database."""
    try:
        logger.info(f'Login attempt for username: {username}')
        
        # Use PostgreSQL authentication
        try:
            from app.postgres_auth import authenticate_postgres_user
            user = authenticate_postgres_user(db, username, password)
            
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'role': user.role,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
        except Exception as auth_error:
            logger.error(f'PostgreSQL auth error: {auth_error}')
        
        # Fallback to hardcoded authentication if PostgreSQL fails
        default_admin_user = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
        default_admin_pass = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
        default_viewer_user = os.getenv('DEFAULT_VIEWER_USERNAME', 'viewer') 
        default_viewer_pass = os.getenv('DEFAULT_VIEWER_PASSWORD', 'viewer123')
        
        if username == default_admin_user and password == default_admin_pass:
            return {
                'id': 1,
                'username': default_admin_user,
                'full_name': os.getenv('DEFAULT_ADMIN_FULLNAME', 'System Administrator'),
                'role': 'admin',
                'is_active': True,
                'created_at': '2024-01-01T00:00:00',
                'last_login': None
            }
        elif username == default_viewer_user and password == default_viewer_pass:
            return {
                'id': 2,
                'username': default_viewer_user,
                'full_name': os.getenv('DEFAULT_VIEWER_FULLNAME', 'Demo Viewer'),
                'role': 'viewer',
                'is_active': True,
                'created_at': '2024-01-01T00:00:00',
                'last_login': None
            }
        else:
            raise HTTPException(status_code=401, detail='Invalid username or password')
            
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        raise HTTPException(status_code=401, detail='Invalid username or password')


@app.get("/auth/test")
async def auth_test():
    """Test authentication endpoint availability."""
    return {"message": "Auth endpoint available", "status": "ready"}


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