from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to Python path for app imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    # Import your main FastAPI app
    from app.main import app as main_app
    
    # Use the main app directly
    app = main_app
    
except ImportError as e:
    # Fallback: Create a minimal FastAPI app if import fails
    app = FastAPI(title="ElectraLens API", version="1.0.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "ElectraLens API is running on Vercel", "error": f"Main app import failed: {str(e)}"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "ElectraLens-Fallback"}