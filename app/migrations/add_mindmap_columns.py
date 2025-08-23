"""
Migration script to add mindmap columns to newsletter table
"""

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from sqlalchemy import create_engine, text, Column, Text, JSON
from app.core.database import create_database_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_mindmap_columns():
    """Add mindmap columns to existing newsletter table"""
    try:
        engine = create_database_engine()
        
        logger.info("Adding mindmap columns to newsletter table...")
        
        with engine.connect() as conn:
            # Check if we're using PostgreSQL or SQLite
            if "postgresql" in str(engine.url):
                # PostgreSQL syntax
                try:
                    # Add mindmap_markdown column
                    conn.execute(text("""
                        ALTER TABLE newsletters 
                        ADD COLUMN IF NOT EXISTS mindmap_markdown TEXT
                    """))
                    logger.info("✅ Added mindmap_markdown column")
                    
                    # Add mindmap_agent_data column
                    conn.execute(text("""
                        ALTER TABLE newsletters 
                        ADD COLUMN IF NOT EXISTS mindmap_agent_data JSON DEFAULT '{}'
                    """))
                    logger.info("✅ Added mindmap_agent_data column")
                    
                except Exception as e:
                    logger.warning(f"Columns might already exist: {e}")
                    
            else:
                # SQLite syntax
                try:
                    # Add mindmap_markdown column
                    conn.execute(text("""
                        ALTER TABLE newsletters 
                        ADD COLUMN mindmap_markdown TEXT
                    """))
                    logger.info("✅ Added mindmap_markdown column")
                    
                except Exception as e:
                    logger.warning(f"mindmap_markdown column might already exist: {e}")
                
                try:
                    # Add mindmap_agent_data column
                    conn.execute(text("""
                        ALTER TABLE newsletters 
                        ADD COLUMN mindmap_agent_data TEXT DEFAULT '{}'
                    """))
                    logger.info("✅ Added mindmap_agent_data column")
                    
                except Exception as e:
                    logger.warning(f"mindmap_agent_data column might already exist: {e}")
            
            # Commit the changes
            conn.commit()
            logger.info("✅ Mindmap columns migration completed successfully!")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding mindmap columns: {e}")
        return False


def verify_mindmap_columns():
    """Verify that mindmap columns exist in the newsletter table"""
    try:
        engine = create_database_engine()
        
        with engine.connect() as conn:
            if "postgresql" in str(engine.url):
                # PostgreSQL query to check columns
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'newsletters' 
                    AND column_name IN ('mindmap_markdown', 'mindmap_agent_data')
                """))
            else:
                # SQLite query to check columns
                result = conn.execute(text("""
                    PRAGMA table_info(newsletters)
                """))
                
            columns = [row[0] for row in result] if "postgresql" in str(engine.url) else [row[1] for row in result]
            
            mindmap_columns = [col for col in columns if 'mindmap' in col]
            
            if mindmap_columns:
                logger.info(f"✅ Found mindmap columns: {', '.join(mindmap_columns)}")
                return True
            else:
                logger.warning("❌ Mindmap columns not found")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error verifying mindmap columns: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "add":
            add_mindmap_columns()
        elif command == "verify":
            verify_mindmap_columns()
        else:
            print("Usage: python add_mindmap_columns.py [add|verify]")
    else:
        add_mindmap_columns()