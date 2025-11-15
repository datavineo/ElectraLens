from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use SQLite for Vercel deployment (reliable and fast)
if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
    DATABASE_URL = 'sqlite:///:memory:'
else:
    # For local development, check for DATABASE_URL or use SQLite
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./voters.db')

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
