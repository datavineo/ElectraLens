import os
import sys

# Set environment variables for Vercel
os.environ.setdefault('VERCEL', '1')
os.environ.setdefault('VERCEL_ENV', 'production')

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import the Vercel-compatible app directly
from app.main_vercel import app

# That's it! Just export the app for Vercel to run with uvicorn