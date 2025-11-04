from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./voters.db')

# Environment-specific database configuration
if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
    # Production: Use PostgreSQL on Vercel
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_aTq54cvMEkiz@ep-orange-sea-ad3n3cx8-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
else:
    # Local development: Use SQLite to avoid psycopg2 build issues
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
