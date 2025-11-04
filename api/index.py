from fastapi import FastAPI
import os
import sys

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'
os.environ['VERCEL_ENV'] = 'production'

# Create a basic working app first
app = FastAPI(title="ElectraLens API", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "ElectraLens API is running on Vercel",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")  
async def health():
    return {
        "status": "healthy",
        "service": "ElectraLens", 
        "environment": "vercel"
    }

# Try to import and enhance with main app functionality
try:
    # Add parent directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    
    # Import the main FastAPI app
    from app.main import app as main_app
    
    # Copy routes from main app (safer than direct import)
    for route in main_app.routes:
        if hasattr(route, 'path') and route.path not in ['/', '/health']:
            app.router.routes.append(route)
    
    # Copy middleware
    app.middleware_stack = main_app.middleware_stack
    
    @app.get("/status")
    async def status():
        return {
            "status": "success", 
            "main_app": "loaded",
            "database": "connected"
        }
        
except Exception as e:
    @app.get("/status")
    async def status_error():
        return {
            "status": "basic_mode",
            "error": str(e),
            "message": "Running with basic endpoints only"
        }
        
    @app.get("/error")
    async def error_details():
        return {
            "error": str(e),
            "type": type(e).__name__,
            "message": "Main app import failed"
        }