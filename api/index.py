from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import your main FastAPI app
from app.main import app as fastapi_app

# Create a new FastAPI app for Vercel
app = FastAPI()

# Mount the original FastAPI app under /api
app.mount("/api", fastapi_app, name="api")

# Serve static files if needed
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "ElectraLens API is running on Vercel", "docs": "/api/docs"}

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ElectraLens"}