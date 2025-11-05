#!/usr/bin/env python3
"""
Vercel Environment Variables Setup Helper
Run this script to generate the exact environment variables needed for Vercel deployment.
"""

import os
from urllib.parse import urlparse

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_env_var(name, value, description=""):
    """Print an environment variable in a formatted way."""
    print(f"Variable: {name}")
    print(f"Value:    {value}")
    if description:
        print(f"Info:     {description}")
    print()

def main():
    print_header("🚀 Vercel Environment Variables - ElectraLens")
    
    print("Copy these environment variables to your Vercel project:")
    print("Dashboard → Your Project → Settings → Environment Variables\n")
    
    print_header("Required Variables")
    
    # Check if .env exists
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Found .env file - using values from there\n")
        
        database_url = os.getenv('DATABASE_URL', 'NOT_SET')
        allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:8501')
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    else:
        print("⚠️  No .env file found - using defaults\n")
        database_url = 'postgresql://user:pass@host:5432/dbname?sslmode=require'
        allowed_origins = 'https://your-streamlit-app.streamlit.app'
        log_level = 'INFO'
    
    # DATABASE_URL
    print_env_var(
        "DATABASE_URL",
        database_url,
        "PostgreSQL connection string (Neon, Heroku, Railway, etc.)"
    )
    
    if 'sqlite' in database_url.lower():
        print("⚠️  WARNING: You're using SQLite. For production, use PostgreSQL!")
        print("   Recommended providers:")
        print("   - Neon (https://neon.tech) - Free tier available")
        print("   - Railway (https://railway.app) - $5/month")
        print("   - Heroku Postgres - Free tier limited\n")
    
    # ALLOWED_ORIGINS
    print_env_var(
        "ALLOWED_ORIGINS",
        allowed_origins,
        "Comma-separated list of allowed frontend URLs"
    )
    
    # LOG_LEVEL
    print_env_var(
        "LOG_LEVEL",
        log_level,
        "Logging verbosity (DEBUG, INFO, WARNING, ERROR)"
    )
    
    print_header("Automatically Set by Vercel")
    
    print("These are set automatically - no action needed:\n")
    print("VERCEL=1")
    print("VERCEL_ENV=production")
    print()
    
    print_header("Streamlit Cloud Secrets")
    
    print("Add this to Streamlit Cloud secrets:")
    print("(Dashboard → Your App → Settings → Secrets)\n")
    print('API_BASE = "https://your-vercel-app.vercel.app"')
    print()
    
    print_header("Quick Setup Commands")
    
    print("1. Install Vercel CLI (optional):")
    print("   npm i -g vercel\n")
    
    print("2. Set environment variables via CLI:")
    print(f'   vercel env add DATABASE_URL')
    print(f'   vercel env add ALLOWED_ORIGINS')
    print(f'   vercel env add LOG_LEVEL\n')
    
    print("3. Or use Vercel Dashboard:")
    print("   https://vercel.com/dashboard → Your Project → Settings → Environment Variables\n")
    
    print_header("Database Setup Options")
    
    print("Option A: Neon (Recommended)\n")
    print("1. Go to: https://neon.tech/")
    print("2. Create account and new project")
    print("3. Copy connection string")
    print("4. Add as DATABASE_URL in Vercel\n")
    
    print("Option B: Railway\n")
    print("1. Go to: https://railway.app/")
    print("2. Create project and add PostgreSQL")
    print("3. Copy DATABASE_URL from variables")
    print("4. Add to Vercel\n")
    
    print("Option C: Heroku Postgres\n")
    print("1. Create Heroku app")
    print("2. Add Heroku Postgres addon")
    print("3. Get DATABASE_URL from Heroku config")
    print("4. Add to Vercel\n")
    
    print_header("Testing Your Deployment")
    
    print("After deployment, test these endpoints:\n")
    print("✓ https://your-app.vercel.app/")
    print("✓ https://your-app.vercel.app/health")
    print("✓ https://your-app.vercel.app/status")
    print("✓ https://your-app.vercel.app/docs")
    print("✓ https://your-app.vercel.app/voters")
    print()
    
    print_header("Next Steps")
    
    print("1. [ ] Fix code issues (requirements.txt, database.py)")
    print("2. [ ] Set up PostgreSQL database (Neon/Railway/Heroku)")
    print("3. [ ] Create Vercel project and connect GitHub")
    print("4. [ ] Add environment variables in Vercel")
    print("5. [ ] Deploy backend to Vercel")
    print("6. [ ] Deploy frontend to Streamlit Cloud")
    print("7. [ ] Update ALLOWED_ORIGINS with Streamlit URL")
    print("8. [ ] Test full application")
    print()
    
    print("="*70)
    print("For detailed instructions, see: VERCEL_DEPLOYMENT_GUIDE.md")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
