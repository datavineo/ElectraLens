from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./voters.db')

# For Vercel deployment, use in-memory SQLite to avoid file system issues
if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
    # Use in-memory SQLite for Vercel deployment (no file system writes)
    DATABASE_URL = 'sqlite:///:memory:'

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
