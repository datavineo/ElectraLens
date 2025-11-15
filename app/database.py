from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Force SQLite for all environments (most reliable for demo)
DATABASE_URL = 'sqlite:///:memory:'

# Log the database URL being used
print(f"🗄️ Database URL: {DATABASE_URL}")

# Override any environment DATABASE_URL that might cause issues
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']
    print("🔧 Removed problematic DATABASE_URL from environment")

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
