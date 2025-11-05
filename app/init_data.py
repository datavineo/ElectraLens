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
        existing_voters = crud.list_voters(db, skip=0, limit=1)
        if existing_voters:
            return  # Data already exists
        
        # Sample voters data - matches current schema
        sample_voters = [
            {
                "name": "John Doe",
                "age": 35,
                "gender": "Male",
                "constituency": "North District",
                "booth_no": "B001",
                "address": "123 Main St, New York, NY",
                "vote": True
            },
            {
                "name": "Jane Smith", 
                "age": 28,
                "gender": "Female",
                "constituency": "South District",
                "booth_no": "B002",
                "address": "456 Oak Ave, Los Angeles, CA",
                "vote": False
            },
            {
                "name": "Mike Johnson",
                "age": 42,
                "gender": "Male",
                "constituency": "East District",
                "booth_no": "B003",
                "address": "789 Pine Rd, Chicago, IL",
                "vote": True
            },
            {
                "name": "Sarah Wilson",
                "age": 31,
                "gender": "Female",
                "constituency": "West District",
                "booth_no": "B004",
                "address": "321 Elm St, Houston, TX",
                "vote": False
            },
            {
                "name": "David Brown",
                "age": 29,
                "gender": "Male",
                "constituency": "Central District",
                "booth_no": "B005",
                "address": "654 Maple Dr, Phoenix, AZ",
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