"""
Database utility functions for Newsletter AI
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import sessionmaker
from app.core.database import create_database_engine, get_db
from app.models import User, Newsletter, UserPreferences, NewsletterHistory
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class DatabaseUtils:
    """Utility class for common database operations"""
    
    def __init__(self):
        self.engine = create_database_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        db = self.get_session()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()
    
    def get_user_with_preferences(self, user_id: str) -> Optional[User]:
        """Get user with their preferences loaded"""
        db = self.get_session()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
    
    def get_user_newsletters(self, user_id: str, limit: int = 10) -> List[Newsletter]:
        """Get user's newsletters ordered by creation date"""
        db = self.get_session()
        try:
            return db.query(Newsletter).filter(
                Newsletter.user_id == user_id
            ).order_by(Newsletter.created_at.desc()).limit(limit).all()
        finally:
            db.close()
    
    def get_newsletter_with_history(self, newsletter_id: str) -> Optional[Newsletter]:
        """Get newsletter with its delivery history"""
        db = self.get_session()
        try:
            return db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
        finally:
            db.close()
    
    def create_user(self, email: str, **kwargs) -> User:
        """Create a new user"""
        db = self.get_session()
        try:
            user = User(email=email, **kwargs)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def update_user_preferences(self, user_id: str, preferences_data: dict) -> bool:
        """Update user preferences"""
        db = self.get_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            if user.preferences:
                # Update existing preferences
                for key, value in preferences_data.items():
                    if hasattr(user.preferences, key):
                        setattr(user.preferences, key, value)
            else:
                # Create new preferences
                prefs = UserPreferences(user_id=user_id, **preferences_data)
                db.add(prefs)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating preferences: {e}")
            return False
        finally:
            db.close()
    
    def create_newsletter(self, user_id: str, newsletter_data: dict) -> Newsletter:
        """Create a new newsletter"""
        db = self.get_session()
        try:
            newsletter = Newsletter(user_id=user_id, **newsletter_data)
            db.add(newsletter)
            db.commit()
            db.refresh(newsletter)
            return newsletter
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def update_newsletter_status(self, newsletter_id: str, status: str) -> bool:
        """Update newsletter status"""
        db = self.get_session()
        try:
            newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
            if not newsletter:
                return False
            
            newsletter.status = status
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating newsletter status: {e}")
            return False
        finally:
            db.close()
    
    def create_newsletter_history(self, user_id: str, newsletter_id: str, history_data: dict) -> NewsletterHistory:
        """Create newsletter history entry"""
        db = self.get_session()
        try:
            history = NewsletterHistory(
                user_id=user_id,
                newsletter_id=newsletter_id,
                **history_data
            )
            db.add(history)
            db.commit()
            db.refresh(history)
            return history
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_database_stats(self) -> dict:
        """Get database statistics"""
        db = self.get_session()
        try:
            stats = {
                'users': db.query(User).count(),
                'newsletters': db.query(Newsletter).count(),
                'preferences': db.query(UserPreferences).count(),
                'history_entries': db.query(NewsletterHistory).count()
            }
            return stats
        finally:
            db.close()

# Global instance
db_utils = DatabaseUtils()

if __name__ == "__main__":
    # Test the utility functions
    utils = DatabaseUtils()
    
    print("📊 Database Statistics:")
    stats = utils.get_database_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n👥 Users:")
    db = utils.get_session()
    users = db.query(User).all()
    for user in users:
        print(f"   {user.email} - {user.first_name} {user.last_name}")
    db.close()