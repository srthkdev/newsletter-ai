#!/usr/bin/env python3
"""
Migration: Add mindmap SVG and keywords data columns

This migration adds the new mindmap_svg and keywords_data columns
to the newsletters table to support enhanced mindmap functionality.
"""

import sys
import os
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.exc import OperationalError
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_mindmap_enhancement_columns():
    """Add mindmap_svg and keywords_data columns to newsletters table"""
    try:
        # Import database configuration
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.core.config import settings
        
        # Create engine and connect
        engine = create_engine(settings.DATABASE_URL)
        logger.info("🔌 Connected to database")
        
        with engine.connect() as conn:
            logger.info("🚀 Starting mindmap enhancement columns migration...")
            
            # Check database type for appropriate syntax
            if "sqlite" in str(engine.url).lower():
                # SQLite syntax
                try:
                    # Add mindmap_svg column
                    conn.execute(text("""
                        ALTER TABLE newsletters 
                        ADD COLUMN mindmap_svg TEXT
                    """))
                    logger.info("✅ Added mindmap_svg column")
                    
                except Exception as e:
                    logger.warning(f"mindmap_svg column might already exist: {e}")
                
                try:
                    # Add keywords_data column (JSON stored as TEXT in SQLite)
                    conn.execute(text("""
                        ALTER TABLE newsletters 
                        ADD COLUMN keywords_data TEXT DEFAULT '{}'
                    """))
                    logger.info("✅ Added keywords_data column")
                    
                except Exception as e:
                    logger.warning(f"keywords_data column might already exist: {e}")
                    
            else:
                # PostgreSQL syntax
                try:
                    # Add mindmap_svg column
                    conn.execute(text("""
                        ALTER TABLE newsletters 
                        ADD COLUMN IF NOT EXISTS mindmap_svg TEXT
                    """))
                    logger.info("✅ Added mindmap_svg column")
                    
                except Exception as e:
                    logger.warning(f"mindmap_svg column might already exist: {e}")
                
                try:
                    # Add keywords_data column
                    conn.execute(text("""
                        ALTER TABLE newsletters 
                        ADD COLUMN IF NOT EXISTS keywords_data JSONB DEFAULT '{}'
                    """))
                    logger.info("✅ Added keywords_data column")
                    
                except Exception as e:
                    logger.warning(f"keywords_data column might already exist: {e}")
            
            # Commit the changes
            conn.commit()
            logger.info("✅ Mindmap enhancement columns migration completed successfully!")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding mindmap enhancement columns: {e}")
        return False

def verify_columns():
    """Verify that the new columns were added successfully"""
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.core.config import settings
        
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Get table info
            metadata = MetaData()
            newsletters_table = Table('newsletters', metadata, autoload_with=engine)
            
            columns = [column.name for column in newsletters_table.columns]
            
            # Check for new columns
            required_columns = ['mindmap_svg', 'keywords_data']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                logger.error(f"❌ Missing columns: {missing_columns}")
                return False
            else:
                logger.info("✅ All mindmap enhancement columns present")
                return True
                
    except Exception as e:
        logger.error(f"❌ Error verifying columns: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Newsletter AI - Mindmap Enhancement Migration")
    print("=" * 50)
    
    # Run migration
    if add_mindmap_enhancement_columns():
        print("✅ Migration completed successfully!")
        
        # Verify migration
        if verify_columns():
            print("✅ Column verification passed!")
        else:
            print("⚠️ Column verification failed")
            sys.exit(1)
    else:
        print("❌ Migration failed!")
        sys.exit(1)
    
    print("🎉 Mindmap enhancement ready!")