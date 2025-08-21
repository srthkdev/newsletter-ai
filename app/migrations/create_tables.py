"""
Database migration script to create all tables for Newsletter AI
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text
from app.core.database import Base, create_database_engine
from app.models import User, Newsletter, UserPreferences, NewsletterHistory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_all_tables():
    """Create all database tables"""
    try:
        engine = create_database_engine()
        
        logger.info("Creating all database tables...")
        
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ All tables created successfully!")
        
        # Verify tables were created
        with engine.connect() as conn:
            # Check if we're using PostgreSQL or SQLite
            if "postgresql" in str(engine.url):
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
            else:
                result = conn.execute(text("""
                    SELECT name 
                    FROM sqlite_master 
                    WHERE type='table'
                """))
            
            tables = [row[0] for row in result]
            logger.info(f"Created tables: {', '.join(tables)}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

def drop_all_tables():
    """Drop all database tables (use with caution!)"""
    try:
        engine = create_database_engine()
        
        logger.warning("⚠️  Dropping all database tables...")
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        
        logger.info("✅ All tables dropped successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        return False

def reset_database():
    """Reset database by dropping and recreating all tables"""
    logger.info("🔄 Resetting database...")
    
    if drop_all_tables():
        return create_all_tables()
    
    return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            create_all_tables()
        elif command == "drop":
            drop_all_tables()
        elif command == "reset":
            reset_database()
        else:
            print("Usage: python create_tables.py [create|drop|reset]")
    else:
        create_all_tables()