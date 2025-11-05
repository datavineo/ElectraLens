"""
Initialize database with default admin user.
Run this script once after setting up the database.
"""
from app.database import SessionLocal, engine
from app import models, crud

def init_admin():
    """Create default admin user if not exists."""
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = crud.get_user_by_username(db, "admin")
        
        if admin_user:
            print("✅ Admin user already exists")
            print(f"   Username: {admin_user.username}")
            print(f"   Role: {admin_user.role}")
            print(f"   Active: {admin_user.is_active}")
        else:
            # Create default admin user
            admin = crud.create_user(
                db=db,
                username="admin",
                password="admin123",
                full_name="System Administrator",
                role="admin"
            )
            print("✅ Default admin user created successfully!")
            print(f"   Username: {admin.username}")
            print(f"   Password: admin123")
            print(f"   Role: {admin.role}")
            print("\n⚠️  IMPORTANT: Please change the default password after first login!")
        
        # Create a demo viewer user
        viewer_user = crud.get_user_by_username(db, "viewer")
        if not viewer_user:
            viewer = crud.create_user(
                db=db,
                username="viewer",
                password="viewer123",
                full_name="Demo Viewer",
                role="viewer"
            )
            print("\n✅ Demo viewer user created successfully!")
            print(f"   Username: {viewer.username}")
            print(f"   Password: viewer123")
            print(f"   Role: {viewer.role}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Initializing database with default users...\n")
    init_admin()
    print("\n✅ Initialization complete!")
