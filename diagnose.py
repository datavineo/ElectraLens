"""
Diagnostic script to identify potential Vercel runtime issues
"""
import sys
import traceback

print("=" * 60)
print("🔍 Vercel Runtime Diagnostic")
print("=" * 60)

# Test 1: Python version
print(f"\n✓ Python version: {sys.version}")

# Test 2: Import core dependencies
print("\n📦 Testing imports...")
try:
    import fastapi
    print(f"  ✓ FastAPI {fastapi.__version__}")
except Exception as e:
    print(f"  ❌ FastAPI: {e}")

try:
    import sqlalchemy
    print(f"  ✓ SQLAlchemy {sqlalchemy.__version__}")
except Exception as e:
    print(f"  ❌ SQLAlchemy: {e}")

try:
    import pydantic
    print(f"  ✓ Pydantic {pydantic.__version__}")
except Exception as e:
    print(f"  ❌ Pydantic: {e}")

# Test 3: Import app modules
print("\n🔧 Testing app modules...")
sys.path.insert(0, '.')

try:
    from app import database
    print("  ✓ app.database imported")
except Exception as e:
    print(f"  ❌ app.database: {e}")
    traceback.print_exc()

try:
    from app import models
    print("  ✓ app.models imported")
except Exception as e:
    print(f"  ❌ app.models: {e}")
    traceback.print_exc()

try:
    from app import schemas
    print("  ✓ app.schemas imported")
except Exception as e:
    print(f"  ❌ app.schemas: {e}")
    traceback.print_exc()

try:
    from app import crud
    print("  ✓ app.crud imported")
except Exception as e:
    print(f"  ❌ app.crud: {e}")
    traceback.print_exc()

# Test 4: Database creation
print("\n💾 Testing database...")
try:
    from app.database import engine, Base
    Base.metadata.create_all(bind=engine)
    print("  ✓ Database tables created")
except Exception as e:
    print(f"  ❌ Database creation: {e}")
    traceback.print_exc()

# Test 5: Sample data initialization
print("\n📊 Testing sample data...")
try:
    from app.init_data import init_sample_data
    init_sample_data()
    print("  ✓ Sample data initialized")
except Exception as e:
    print(f"  ❌ Sample data: {e}")
    traceback.print_exc()

# Test 6: FastAPI app creation
print("\n🚀 Testing FastAPI app...")
try:
    from api.index import app
    print("  ✓ FastAPI app created successfully")
    print(f"  ✓ App title: {app.title}")
    print(f"  ✓ Number of routes: {len(app.routes)}")
except Exception as e:
    print(f"  ❌ FastAPI app: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Diagnostic complete!")
print("=" * 60)
