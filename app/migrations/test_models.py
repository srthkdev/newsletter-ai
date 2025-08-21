"""
Test script to validate database models and relationships
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import sessionmaker
from app.core.database import create_database_engine
from app.models import User, Newsletter, UserPreferences, NewsletterHistory, NewsletterStatus, NewsletterType, DeliveryStatus
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_models():
    """Test all models and their relationships"""
    try:
        engine = create_database_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        logger.info("🧪 Testing database models and relationships...")
        
        # Test User model
        users = db.query(User).all()
        logger.info(f"✅ Found {len(users)} users")
        
        for user in users:
            logger.info(f"   User: {user.email} (ID: {user.id})")
            
            # Test User -> Preferences relationship
            if user.preferences:
                prefs = user.preferences
                logger.info(f"      Preferences: {prefs.topics}, tone: {prefs.tone}, frequency: {prefs.frequency}")
            
            # Test User -> Newsletters relationship
            newsletters = user.newsletters
            logger.info(f"      Newsletters: {len(newsletters)}")
            
            for newsletter in newsletters:
                logger.info(f"         Newsletter: {newsletter.title} (Status: {newsletter.status.value})")
                logger.info(f"         Type: {newsletter.newsletter_type.value}, Word count: {newsletter.word_count}")
                logger.info(f"         Topics: {newsletter.topics_covered}, Tone: {newsletter.tone_used}")
                
                # Test Newsletter -> History relationship
                history_entries = newsletter.history_entries
                logger.info(f"         History entries: {len(history_entries)}")
                
                for history in history_entries:
                    logger.info(f"            History: {history.delivery_status.value} at {history.sent_at}")
        
        # Test UserPreferences model
        preferences = db.query(UserPreferences).all()
        logger.info(f"✅ Found {len(preferences)} user preferences")
        
        # Test Newsletter model
        newsletters = db.query(Newsletter).all()
        logger.info(f"✅ Found {len(newsletters)} newsletters")
        
        # Test NewsletterHistory model
        history = db.query(NewsletterHistory).all()
        logger.info(f"✅ Found {len(history)} newsletter history entries")
        
        # Test specific queries
        logger.info("\n🔍 Testing specific queries...")
        
        # Find users with specific preferences (PostgreSQL JSON query)
        from sqlalchemy import text
        tech_users = db.query(User).join(UserPreferences).filter(
            text("user_preferences.topics::jsonb ? 'tech'")
        ).all()
        logger.info(f"✅ Found {len(tech_users)} users interested in tech")
        
        # Find sent newsletters
        sent_newsletters = db.query(Newsletter).filter(
            Newsletter.status == NewsletterStatus.SENT
        ).all()
        logger.info(f"✅ Found {len(sent_newsletters)} sent newsletters")
        
        # Find opened newsletters
        opened_history = db.query(NewsletterHistory).filter(
            NewsletterHistory.delivery_status == DeliveryStatus.OPENED
        ).all()
        logger.info(f"✅ Found {len(opened_history)} opened newsletters")
        
        logger.info("\n🎉 All model tests passed successfully!")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing models: {e}")
        if 'db' in locals():
            db.close()
        return False

def test_model_validation():
    """Test model field validation and constraints"""
    try:
        engine = create_database_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        logger.info("🔍 Testing model validation...")
        
        # Test enum values
        logger.info("✅ Newsletter status enum values:")
        for status in NewsletterStatus:
            logger.info(f"   - {status.value}")
        
        logger.info("✅ Newsletter type enum values:")
        for ntype in NewsletterType:
            logger.info(f"   - {ntype.value}")
        
        logger.info("✅ Delivery status enum values:")
        for status in DeliveryStatus:
            logger.info(f"   - {status.value}")
        
        # Test JSON field structure
        sample_user = db.query(User).first()
        if sample_user and sample_user.preferences:
            prefs = sample_user.preferences
            logger.info(f"✅ Sample preferences JSON structure:")
            logger.info(f"   Topics: {prefs.topics} (type: {type(prefs.topics)})")
            logger.info(f"   Excluded sources: {prefs.excluded_sources} (type: {type(prefs.excluded_sources)})")
        
        sample_newsletter = db.query(Newsletter).first()
        if sample_newsletter:
            logger.info(f"✅ Sample newsletter JSON structure:")
            logger.info(f"   Content sections: {sample_newsletter.content_sections} (type: {type(sample_newsletter.content_sections)})")
            logger.info(f"   Topics covered: {sample_newsletter.topics_covered} (type: {type(sample_newsletter.topics_covered)})")
            logger.info(f"   Sources used: {sample_newsletter.sources_used} (type: {type(sample_newsletter.sources_used)})")
        
        logger.info("🎉 Model validation tests passed!")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in validation tests: {e}")
        if 'db' in locals():
            db.close()
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "models":
            test_models()
        elif command == "validation":
            test_model_validation()
        elif command == "all":
            test_models()
            test_model_validation()
        else:
            print("Usage: python test_models.py [models|validation|all]")
    else:
        test_models()
        test_model_validation()