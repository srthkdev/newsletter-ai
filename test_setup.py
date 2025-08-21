#!/usr/bin/env python3
"""
Test script to verify the FastAPI setup
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all core modules can be imported"""
    try:
        from app.main import app
        print("✓ FastAPI app imported successfully")
        
        from app.core.config import settings
        print("✓ Settings imported successfully")
        
        from app.core.database import Base, get_db
        print("✓ Database components imported successfully")
        
        from app.models.user import User
        from app.models.preferences import UserPreferences
        from app.models.newsletter import Newsletter
        print("✓ Models imported successfully")
        
        from app.schemas.user import User as UserSchema
        from app.schemas.preferences import Preferences
        from app.schemas.newsletter import Newsletter as NewsletterSchema
        print("✓ Schemas imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_fastapi_routes():
    """Test that FastAPI routes are properly configured"""
    try:
        from app.main import app
        routes = [route.path for route in app.routes]
        print(f"✓ Available routes: {routes}")
        return True
    except Exception as e:
        print(f"✗ Route test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Newsletter AI setup...")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_fastapi_routes()
    
    print("=" * 50)
    if success:
        print("✓ All tests passed! Setup is working correctly.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Check the errors above.")
        sys.exit(1)