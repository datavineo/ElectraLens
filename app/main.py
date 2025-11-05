from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, get_db
from .logging_config import setup_logging, logger
import os
import time
from starlette.requests import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from typing import Dict, Any, TYPE_CHECKING

# Conditional import for extractor (only for non-Vercel environments)
if not os.getenv('VERCEL'):
    try:
        from extract.extractor import process_uploaded_pdf, load_csv_into_db  # type: ignore[assignment]
    except ImportError:
        def process_uploaded_pdf(*args: Any, **kwargs: Any) -> Dict[str, str]:
            return {"error": "PDF processing not available"}
        def load_csv_into_db(*args: Any, **kwargs: Any) -> Dict[str, str]:  # type: ignore[misc]
            return {"error": "CSV processing not available"}
else:
    def process_uploaded_pdf(*args: Any, **kwargs: Any) -> Dict[str, str]:
        return {"error": "PDF processing not available in serverless environment"}
    def load_csv_into_db(*args: Any, **kwargs: Any) -> Dict[str, str]:  # type: ignore[misc]
        return {"error": "CSV processing not available in serverless environment"}

# Load environment variables
load_dotenv()


# Initialize logging
setup_logging()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='ElectraLens API - Voter Management System', version='1.0.0')

# Initialize sample data for Vercel (in-memory database)
if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
    try:
        from .init_data import init_sample_data
        init_sample_data()
    except Exception as e:
        logger.warning(f"Could not initialize sample data: {e}")

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler."""
    client_host = request.client.host if request.client else 'unknown'
    logger.warning(f'Rate limit exceeded: {client_host}')
    return JSONResponse(
        status_code=429,
        content={'detail': 'Rate limit exceeded. Maximum 100 requests per minute.'},
    )


# Get allowed origins from env or default
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:8501,http://localhost:3000').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['*'],
)


# Middleware for request/response logging
@app.middleware('http')
async def log_requests(request: Request, call_next):
    """Log all requests and responses with timing."""
    start_time = time.time()
    
    # Log incoming request
    client_host = request.client.host if request.client else 'unknown'
    logger.info(f'{request.method} {request.url.path} - Client: {client_host}')
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response with status and timing
        logger.info(
            f'{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s'
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f'{request.method} {request.url.path} - Error: {str(e)} - Time: {process_time:.3f}s',
            exc_info=True
        )
        raise


# Root and utility endpoints
@app.get('/')
async def root():
    """Root endpoint - API information."""
    return {
        'message': 'ElectraLens API - Voter Management System',
        'version': '1.0.0',
        'status': 'running',
        'docs': '/docs',
        'redoc': '/redoc',
        'endpoints': {
            'voters': '/voters',
            'health': '/health',
            'status': '/status'
        }
    }


@app.get('/health')
async def health():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'service': 'ElectraLens API',
        'version': '1.0.0'
    }


@app.get('/status')
async def status(db: Session = Depends(get_db)):
    """Status endpoint with database check."""
    try:
        # Quick DB check
        voter_count = crud.count_voters(db)
        return {
            'status': 'operational',
            'database': 'connected',
            'voter_count': voter_count,
            'environment': 'vercel' if os.getenv('VERCEL') else 'local'
        }
    except Exception as e:
        logger.error(f'Status check failed: {e}')
        return {
            'status': 'degraded',
            'database': 'error',
            'error': str(e),
            'environment': 'vercel' if os.getenv('VERCEL') else 'local'
        }


@app.post('/voters', response_model=schemas.VoterOut)
@limiter.limit('100/minute')
def create_voter(request: Request, v: schemas.VoterCreate, db: Session = Depends(get_db)):
    """Create a new voter record. (100 req/min limit)"""
    voter = crud.create_voter(db, v)
    logger.info(f'Voter created: ID={voter.id}, Name={voter.name}, Constituency={voter.constituency}')
    return voter


@app.get('/voters', response_model=list[schemas.VoterOut])
@limiter.limit('200/minute')
def list_voters(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List voters with pagination. (200 req/min limit)"""
    voters = crud.list_voters(db, skip=skip, limit=limit)
    logger.debug(f'Listed voters: skip={skip}, limit={limit}, returned={len(voters)}')
    return voters


@app.get('/voters/summary')
def voters_summary(db: Session = Depends(get_db)):
    """Get summary of voters by constituency."""
    summary = crud.summary_by_constituency(db)
    logger.debug(f'Generated summary: {len(summary)} constituencies')
    return summary


@app.get('/voters/constituency/{name}', response_model=list[schemas.VoterOut])
def voters_in_constituency(name: str, db: Session = Depends(get_db)):
    """Get voters in a specific constituency."""
    voters = crud.voters_in_constituency(db, name)
    logger.debug(f'Retrieved voters for constituency: {name}, count={len(voters)}')
    return voters


@app.get('/voters/age-distribution')
def age_dist(db: Session = Depends(get_db)):
    """Get age distribution histogram."""
    distribution = crud.age_distribution(db)
    logger.debug(f'Generated age distribution: {distribution}')
    return distribution


@app.get('/voters/gender-ratio')
def gender_ratio(db: Session = Depends(get_db)):
    """Get gender ratio."""
    ratio = crud.gender_ratio(db)
    logger.debug(f'Generated gender ratio: {ratio}')
    return ratio


@app.put('/voters/{voter_id}', response_model=schemas.VoterOut)
@limiter.limit('100/minute')
def update_voter(request: Request, voter_id: int, v: schemas.VoterUpdate, db: Session = Depends(get_db)):
    """Update a voter record. (100 req/min limit)"""
    updated = crud.update_voter(db, voter_id, v)
    if not updated:
        logger.warning(f'Update failed: Voter ID {voter_id} not found')
        raise HTTPException(status_code=404, detail='Voter not found')
    logger.info(f'Voter updated: ID={voter_id}, Name={updated.name}')
    return updated


@app.delete('/voters/{voter_id}')
@limiter.limit('100/minute')
def delete_voter(request: Request, voter_id: int, db: Session = Depends(get_db)):
    """Delete a voter record. (100 req/min limit)"""
    ok = crud.delete_voter(db, voter_id)
    if not ok:
        logger.warning(f'Delete failed: Voter ID {voter_id} not found')
        raise HTTPException(status_code=404, detail='Voter not found')
    logger.info(f'Voter deleted: ID={voter_id}')
    return {'ok': True}


@app.get('/voters/search', response_model=list[schemas.VoterOut])
@limiter.limit('150/minute')
def search_voters_endpoint(request: Request, q: str, limit: int = 100, db: Session = Depends(get_db)):
    """Search voters by name, constituency, or booth number. (150 req/min limit)"""
    if len(q) < 2:
        logger.warning(f'Search query too short: "{q}"')
        raise HTTPException(status_code=400, detail='Search query must be at least 2 characters')
    voters = crud.search_voters(db, q, limit)
    logger.info(f'Searched voters: query="{q}", results={len(voters)}')
    return voters


@app.get('/voters/filter/constituency', response_model=list[schemas.VoterOut])
def filter_constituency(constituency: str, limit: int = 100, db: Session = Depends(get_db)):
    """Filter voters by constituency."""
    voters = crud.filter_by_constituency(db, constituency, limit)
    logger.debug(f'Filtered by constituency: {constituency}, results={len(voters)}')
    return voters


@app.get('/voters/filter/gender', response_model=list[schemas.VoterOut])
def filter_gender(gender: str, limit: int = 100, db: Session = Depends(get_db)):
    """Filter voters by gender."""
    voters = crud.filter_by_gender(db, gender, limit)
    logger.debug(f'Filtered by gender: {gender}, results={len(voters)}')
    return voters


@app.get('/voters/filter/age-range', response_model=list[schemas.VoterOut])
def filter_age_range(min_age: int, max_age: int, limit: int = 100, db: Session = Depends(get_db)):
    """Filter voters by age range."""
    if min_age < 0 or max_age > 150 or min_age > max_age:
        logger.warning(f'Invalid age range: min={min_age}, max={max_age}')
        raise HTTPException(status_code=400, detail='Invalid age range')
    voters = crud.filter_by_age_range(db, min_age, max_age, limit)
    logger.debug(f'Filtered by age range: {min_age}-{max_age}, results={len(voters)}')
    return voters


@app.post('/upload_pdf')
@limiter.limit('20/minute')
def upload_pdf(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload PDF, extract tables, and load into database. (20 req/min limit)"""
    file_size = len(file.file.read())
    file.file.seek(0)  # Reset file pointer
    logger.info(f'PDF upload started: filename={file.filename}, size={file_size} bytes')
    
    # save uploaded file to temp and process
    contents = file.file.read()
    # write to a temp file
    import tempfile
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp.write(contents)
    tmp.close()
    
    try:
        csv_path = process_uploaded_pdf(tmp.name)
        logger.info(f'PDF extraction successful: output={csv_path}')
        
        load_csv_into_db(csv_path, db)
        logger.info(f'CSV loaded into database: file={csv_path}')
        
        return {'uploaded': True, 'csv': csv_path}
    except Exception as e:
        logger.error(f'PDF processing failed: {str(e)}', exc_info=True)
        raise HTTPException(status_code=400, detail=f'PDF processing failed: {str(e)}')


# ============= AUTHENTICATION ENDPOINTS =============

@app.post('/auth/login')
@limiter.limit('10/minute')
def login(request: Request, username: str, password: str, db: Session = Depends(get_db)):
    """Authenticate user and return user details."""
    logger.info(f'Login attempt for username: {username}')
    
    user = crud.authenticate_user(db, username, password)
    if not user:
        logger.warning(f'Failed login attempt for username: {username}')
        raise HTTPException(status_code=401, detail='Invalid username or password')
    
    logger.info(f'Successful login: user_id={user.id}, username={username}, role={user.role}')
    
    return {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'role': user.role,
        'last_login': user.last_login
    }


@app.post('/auth/users')
@limiter.limit('5/minute')
def create_new_user(
    request: Request,
    username: str,
    password: str,
    full_name: str = "",
    role: str = "viewer",
    db: Session = Depends(get_db)
):
    """Create a new user (admin only in production)."""
    # Check if username already exists
    existing_user = crud.get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(status_code=400, detail='Username already exists')
    
    # Validate role
    if role not in ['admin', 'viewer']:
        raise HTTPException(status_code=400, detail='Role must be either admin or viewer')
    
    user = crud.create_user(db, username, password, full_name, role)
    logger.info(f'New user created: username={username}, role={role}')
    
    return {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'role': user.role,
        'created_at': user.created_at
    }


@app.get('/auth/users')
@limiter.limit('30/minute')
def get_all_users(request: Request, db: Session = Depends(get_db)):
    """Get list of all users."""
    users = crud.list_users(db)
    return [
        {
            'id': u.id,
            'username': u.username,
            'full_name': u.full_name,
            'role': u.role,
            'is_active': u.is_active,
            'created_at': u.created_at,
            'last_login': u.last_login
        }
        for u in users
    ]


@app.put('/auth/users/{user_id}')
@limiter.limit('20/minute')
def update_user_details(
    request: Request,
    user_id: int,
    full_name: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db)
):
    """Update user details."""
    user = crud.update_user(db, user_id, full_name, role, is_active)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    logger.info(f'User updated: user_id={user_id}')
    return {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'role': user.role,
        'is_active': user.is_active
    }


@app.delete('/auth/users/{user_id}')
@limiter.limit('10/minute')
def delete_user_account(request: Request, user_id: int, db: Session = Depends(get_db)):
    """Delete a user account."""
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail='User not found')
    
    logger.info(f'User deleted: user_id={user_id}')
    return {'deleted': True}
