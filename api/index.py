from fastapi import FastAPI
import os
import sys

# Set environment variables for Vercel
os.environ.setdefault('VERCEL', '1')
os.environ.setdefault('VERCEL_ENV', 'production')

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Create a minimal working app first
app = FastAPI(title="ElectraLens API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "ElectraLens API is running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "environment": "vercel"}

# Try to import and enhance with main features
try:
    from app.main_vercel import app as main_app
    # Copy all routes from main app
    app.router.routes.extend(main_app.router.routes)
    app.middleware_stack = main_app.middleware_stack
    
except Exception as e:
    @app.get("/error")
    async def error_info():
        return {"error": str(e), "message": "Running in basic mode"}

# Fallback endpoints if main app fails
@app.get("/api/status")
async def api_status():
    return {"status": "running", "mode": "vercel", "timestamp": "2025-11-04"}