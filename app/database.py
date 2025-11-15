from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use PostgreSQL from environment or fallback to SQLite for local dev
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./electralens.db')

# Log the database URL being used (hide password for security)
if DATABASE_URL.startswith('postgresql://'):
    # Hide password in logs
    url_parts = DATABASE_URL.split('@')
    if len(url_parts) > 1:
        masked_url = f"{url_parts[0].split(':')[0]}://***:***@{url_parts[1]}"
        print(f"[DB] Using PostgreSQL: {masked_url}")
    else:
        print("[DB] Using PostgreSQL database")
else:
    print(f"[DB] Database URL: {DATABASE_URL}")

if DATABASE_URL.startswith('postgresql://'):
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Set to True for SQL debugging
    )
elif DATABASE_URL.startswith('sqlite'):
    # SQLite configuration  
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Fallback configuration
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
