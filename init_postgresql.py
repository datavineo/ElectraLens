"""
Database initialization script for PostgreSQL production environment.
This script will create all tables and initialize default users and sample data.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.database import engine, SessionLocal
from app import models, crud, schemas
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_postgresql_database():
    """Initialize PostgreSQL database with tables, users, and sample data."""
    
    logger.info("🔧 Starting PostgreSQL database initialization...")
    
    try:
        # Create all tables
        logger.info("Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Initialize with session
        db = SessionLocal()
        
        try:
            # Create default admin user
            logger.info("Creating default users...")
            
            admin_user = crud.get_user_by_username(db, "admin")
            if not admin_user:
                try:
                    admin = crud.create_user(
                        db=db,
                        username="admin",
                        password="admin123",
                        full_name="System Administrator",
                        role="admin"
                    )
                    logger.info("✅ Admin user created successfully")
                except Exception as e:
                    logger.warning(f"Admin user creation failed (may already exist): {e}")
            else:
                logger.info("✅ Admin user already exists")
            
            # Create default viewer user
            viewer_user = crud.get_user_by_username(db, "viewer")
            if not viewer_user:
                try:
                    viewer = crud.create_user(
                        db=db,
                        username="viewer",
                        password="viewer123",
                        full_name="Demo Viewer",
                        role="viewer"
                    )
                    logger.info("✅ Viewer user created successfully")
                except Exception as e:
                    logger.warning(f"Viewer user creation failed (may already exist): {e}")
            else:
                logger.info("✅ Viewer user already exists")
            
            # Initialize sample data
            logger.info("Checking for existing voter data...")
            existing_voters = crud.list_voters(db, skip=0, limit=1)
            
            if not existing_voters:
                logger.info("Creating sample voter data...")
                
                sample_voters = [
                    {
                        "name": "John Doe",
                        "age": 35,
                        "gender": "Male",
                        "constituency": "North District",
                        "booth_no": "B001",
                        "address": "123 Main St, New York, NY 10001",
                        "vote": True
                    },
                    {
                        "name": "Jane Smith", 
                        "age": 28,
                        "gender": "Female",
                        "constituency": "South District",
                        "booth_no": "B002",
                        "address": "456 Oak Ave, Los Angeles, CA 90210",
                        "vote": False
                    },
                    {
                        "name": "Mike Johnson",
                        "age": 42,
                        "gender": "Male",
                        "constituency": "East District",
                        "booth_no": "B003",
                        "address": "789 Pine Rd, Chicago, IL 60601",
                        "vote": True
                    },
                    {
                        "name": "Sarah Wilson",
                        "age": 31,
                        "gender": "Female",
                        "constituency": "West District",
                        "booth_no": "B004",
                        "address": "321 Elm St, Houston, TX 77001",
                        "vote": False
                    },
                    {
                        "name": "David Brown",
                        "age": 29,
                        "gender": "Male",
                        "constituency": "Central District",
                        "booth_no": "B005",
                        "address": "654 Maple Dr, Phoenix, AZ 85001",
                        "vote": True
                    },
                    {
                        "name": "Emily Davis",
                        "age": 26,
                        "gender": "Female", 
                        "constituency": "North District",
                        "booth_no": "B006",
                        "address": "987 Cedar Lane, Seattle, WA 98101",
                        "vote": True
                    },
                    {
                        "name": "Robert Miller",
                        "age": 55,
                        "gender": "Male",
                        "constituency": "South District", 
                        "booth_no": "B007",
                        "address": "246 Birch Ave, Miami, FL 33101",
                        "vote": False
                    },
                    {
                        "name": "Lisa Garcia",
                        "age": 33,
                        "gender": "Female",
                        "constituency": "East District",
                        "booth_no": "B008", 
                        "address": "135 Willow St, Denver, CO 80201",
                        "vote": True
                    },
                    {
                        "name": "Thomas Anderson",
                        "age": 45,
                        "gender": "Male",
                        "constituency": "West District",
                        "booth_no": "B009",
                        "address": "468 Spruce Rd, Boston, MA 02101",
                        "vote": True
                    },
                    {
                        "name": "Jennifer Martinez",
                        "age": 39,
                        "gender": "Female",
                        "constituency": "Central District",
                        "booth_no": "B010",
                        "address": "579 Fir Blvd, San Francisco, CA 94101",
                        "vote": False
                    }
                ]
                
                # Create sample voters
                for voter_data in sample_voters:
                    try:
                        voter = schemas.VoterCreate(**voter_data)
                        crud.create_voter(db=db, voter=voter)
                    except Exception as e:
                        logger.warning(f"Failed to create voter {voter_data['name']}: {e}")
                
                logger.info(f"✅ Created {len(sample_voters)} sample voters")
            else:
                logger.info(f"✅ Found existing voter data ({len(existing_voters)} voters)")
            
            # Commit all changes
            db.commit()
            
            # Verify the initialization
            total_voters = len(crud.list_voters(db, skip=0, limit=1000))
            admin_count = len([u for u in [crud.get_user_by_username(db, "admin")] if u])
            viewer_count = len([u for u in [crud.get_user_by_username(db, "viewer")] if u])
            
            logger.info("🎉 Database initialization completed successfully!")
            logger.info(f"📊 Summary:")
            logger.info(f"   - Total voters: {total_voters}")
            logger.info(f"   - Admin users: {admin_count}")
            logger.info(f"   - Viewer users: {viewer_count}")
            
        except Exception as e:
            logger.error(f"❌ Error during data initialization: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    init_postgresql_database()