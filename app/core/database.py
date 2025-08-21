from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine for Neon PostgreSQL
def create_database_engine():
    """Create database engine with fallback to SQLite for development"""
    database_url = settings.DATABASE_URL
    
    if not database_url:
        # Fallback to SQLite for local development
        database_url = "sqlite:///./newsletter_ai.db"
        print("⚠️  No DATABASE_URL configured, using SQLite for development")
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
    
    # Use PostgreSQL (Neon)
    return create_engine(
        database_url,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=False           # Set to True for SQL debugging
    )

engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)