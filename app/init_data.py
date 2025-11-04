"""
Initialize sample data for demonstration purposes
"""
from app.database import SessionLocal
from app import models, schemas, crud

def init_sample_data():
    """Initialize sample voters for demonstration"""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_voters = crud.get_voters(db, skip=0, limit=1)
        if existing_voters:
            return  # Data already exists
        
        # Sample voters data
        sample_voters = [
            {
                "name": "John Doe",
                "age": 35,
                "address": "123 Main St, New York, NY",
                "phone": "555-0123",
                "email": "john.doe@email.com",
                "vote": True
            },
            {
                "name": "Jane Smith", 
                "age": 28,
                "address": "456 Oak Ave, Los Angeles, CA",
                "phone": "555-0456",
                "email": "jane.smith@email.com",
                "vote": False
            },
            {
                "name": "Mike Johnson",
                "age": 42,
                "address": "789 Pine Rd, Chicago, IL", 
                "phone": "555-0789",
                "email": "mike.johnson@email.com",
                "vote": True
            },
            {
                "name": "Sarah Wilson",
                "age": 31,
                "address": "321 Elm St, Houston, TX",
                "phone": "555-0321", 
                "email": "sarah.wilson@email.com",
                "vote": False
            },
            {
                "name": "David Brown",
                "age": 29,
                "address": "654 Maple Dr, Phoenix, AZ",
                "phone": "555-0654",
                "email": "david.brown@email.com", 
                "vote": True
            }
        ]
        
        # Create sample voters
        for voter_data in sample_voters:
            voter = schemas.VoterCreate(**voter_data)
            crud.create_voter(db=db, voter=voter)
            
        print("✅ Sample data initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data()