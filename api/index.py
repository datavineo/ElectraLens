import os
import sys

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'
os.environ['VERCEL_ENV'] = 'production'

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import the main FastAPI app directly
from app.main import app