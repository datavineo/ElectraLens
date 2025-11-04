#!/usr/bin/env python3
"""
Simple script to run the API locally for testing
"""
import uvicorn
import os

if __name__ == "__main__":
    # Set environment to use PostgreSQL for local development
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    # For local development, don't set VERCEL env vars
    if 'VERCEL' in os.environ:
        del os.environ['VERCEL']
    if 'VERCEL_ENV' in os.environ:
        del os.environ['VERCEL_ENV']
    
    # Run the API
    uvicorn.run(
        "app.main_vercel:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )