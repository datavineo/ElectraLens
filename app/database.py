from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./voters.db')

# For Vercel deployment, default to SQLite if PostgreSQL URL is provided
# This avoids psycopg2 build issues on Vercel
if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
    # Use SQLite for Vercel deployment to avoid build issues
    DATABASE_URL = 'sqlite:///./voters.db'

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
