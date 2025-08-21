"""
Seed data script for Newsletter AI testing
"""

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from sqlalchemy.orm import sessionmaker
from app.core.database import create_database_engine
from app.models import (
    User,
    Newsletter,
    UserPreferences,
    NewsletterHistory,
    NewsletterStatus,
    NewsletterType,
    DeliveryStatus,
)
from datetime import datetime, timedelta
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_seed_data():
    """Create seed data for testing"""
    try:
        engine = create_database_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        logger.info("Creating seed data...")

        # Create test users
        test_users = [
            {
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "timezone": "America/New_York",
                "is_active": True,
            },
            {
                "email": "jane.smith@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "timezone": "America/Los_Angeles",
                "is_active": True,
            },
            {
                "email": "tech.enthusiast@example.com",
                "first_name": "Alex",
                "last_name": "Tech",
                "timezone": "UTC",
                "is_active": True,
            },
        ]

        created_users = []
        for user_data in test_users:
            # Check if user already exists
            existing_user = (
                db.query(User).filter(User.email == user_data["email"]).first()
            )
            if existing_user:
                logger.info(f"User {user_data['email']} already exists, skipping...")
                created_users.append(existing_user)
                continue

            user = User(**user_data)
            db.add(user)
            db.flush()  # Get the ID
            created_users.append(user)
            logger.info(f"Created user: {user.email}")

        # Create user preferences
        preferences_data = [
            {
                "user": created_users[0],
                "topics": ["tech", "ai", "startups"],
                "tone": "professional",
                "frequency": "daily",
                "preferred_length": "medium",
                "include_summaries": True,
                "preferred_send_time": "09:00",
                "max_articles_per_newsletter": 5,
            },
            {
                "user": created_users[1],
                "topics": ["business", "finance", "marketing"],
                "tone": "casual",
                "frequency": "weekly",
                "preferred_length": "long",
                "include_summaries": True,
                "preferred_send_time": "08:00",
                "max_articles_per_newsletter": 7,
            },
            {
                "user": created_users[2],
                "topics": ["tech", "science", "ai", "programming"],
                "tone": "technical",
                "frequency": "every_2_days",
                "preferred_length": "short",
                "include_summaries": False,
                "preferred_send_time": "18:00",
                "max_articles_per_newsletter": 3,
            },
        ]

        for pref_data in preferences_data:
            user = pref_data.pop("user")

            # Check if preferences already exist
            existing_prefs = (
                db.query(UserPreferences)
                .filter(UserPreferences.user_id == user.id)
                .first()
            )
            if existing_prefs:
                logger.info(f"Preferences for {user.email} already exist, skipping...")
                continue

            preferences = UserPreferences(user_id=user.id, **pref_data)
            db.add(preferences)
            logger.info(f"Created preferences for: {user.email}")

        # Create sample newsletters
        sample_newsletters = [
            {
                "user": created_users[0],
                "title": "AI Breakthroughs This Week",
                "subtitle": "Latest developments in artificial intelligence",
                "introduction": "This week has been exciting for AI enthusiasts...",
                "main_content": "Here are the top AI stories that caught our attention...",
                "conclusion": "The future of AI continues to evolve rapidly...",
                "content_sections": [
                    {
                        "type": "section",
                        "title": "OpenAI Updates",
                        "content": "OpenAI announced new features...",
                    },
                    {
                        "type": "section",
                        "title": "Google AI News",
                        "content": "Google's latest AI research...",
                    },
                ],
                "status": NewsletterStatus.SENT,
                "newsletter_type": NewsletterType.AUTOMATED,
                "topics_covered": ["ai", "tech"],
                "tone_used": "professional",
                "word_count": 850,
                "estimated_read_time": 4,
                "subject_line": "🤖 AI Breakthroughs This Week",
                "sent_at": datetime.utcnow() - timedelta(days=1),
            },
            {
                "user": created_users[1],
                "title": "Business Trends Weekly",
                "subtitle": "Your weekly dose of business insights",
                "introduction": "Welcome to your weekly business roundup...",
                "main_content": "This week's business landscape has been dynamic...",
                "conclusion": "Stay tuned for more business insights next week...",
                "content_sections": [
                    {
                        "type": "section",
                        "title": "Market Updates",
                        "content": "Stock markets showed...",
                    },
                    {
                        "type": "section",
                        "title": "Startup News",
                        "content": "Several startups raised funding...",
                    },
                ],
                "status": NewsletterStatus.SENT,
                "newsletter_type": NewsletterType.AUTOMATED,
                "topics_covered": ["business", "finance"],
                "tone_used": "casual",
                "word_count": 1200,
                "estimated_read_time": 6,
                "subject_line": "📈 Business Trends Weekly",
                "sent_at": datetime.utcnow() - timedelta(days=3),
            },
            {
                "user": created_users[2],
                "title": "Tech Deep Dive",
                "subtitle": "Technical insights for developers",
                "introduction": "Let's dive into the technical details...",
                "main_content": "This edition covers advanced programming concepts...",
                "conclusion": "Keep coding and stay curious...",
                "content_sections": [
                    {
                        "type": "section",
                        "title": "New Frameworks",
                        "content": "Several new frameworks were released...",
                    },
                    {
                        "type": "section",
                        "title": "Performance Tips",
                        "content": "Here are some optimization techniques...",
                    },
                ],
                "status": NewsletterStatus.READY,
                "newsletter_type": NewsletterType.CUSTOM_PROMPT,
                "topics_covered": ["programming", "tech"],
                "tone_used": "technical",
                "word_count": 600,
                "estimated_read_time": 3,
                "subject_line": "⚡ Tech Deep Dive",
                "custom_prompt": "Create a technical newsletter about new programming frameworks",
            },
        ]

        created_newsletters = []
        for newsletter_data in sample_newsletters:
            user = newsletter_data.pop("user")
            newsletter = Newsletter(user_id=user.id, **newsletter_data)
            db.add(newsletter)
            db.flush()  # Get the ID
            created_newsletters.append(newsletter)
            logger.info(f"Created newsletter: {newsletter.title}")

        # Create newsletter history entries
        for i, newsletter in enumerate(
            created_newsletters[:2]
        ):  # Only for sent newsletters
            history = NewsletterHistory(
                user_id=newsletter.user_id,
                newsletter_id=newsletter.id,
                delivery_status=DeliveryStatus.OPENED,
                email_address=created_users[i].email,
                subject_line=newsletter.subject_line,
                message_id=f"msg_{uuid.uuid4().hex[:8]}",
                sent_at=newsletter.sent_at,
                delivered_at=newsletter.sent_at + timedelta(minutes=2),
                opened_at=newsletter.sent_at + timedelta(hours=1),
                open_count=1,
                email_service_used="resend",
            )
            db.add(history)
            logger.info(f"Created history entry for newsletter: {newsletter.title}")

        # Commit all changes
        db.commit()
        logger.info("✅ Seed data created successfully!")

        # Print summary
        user_count = db.query(User).count()
        newsletter_count = db.query(Newsletter).count()
        preferences_count = db.query(UserPreferences).count()
        history_count = db.query(NewsletterHistory).count()

        logger.info(f"📊 Database summary:")
        logger.info(f"   Users: {user_count}")
        logger.info(f"   Newsletters: {newsletter_count}")
        logger.info(f"   User Preferences: {preferences_count}")
        logger.info(f"   Newsletter History: {history_count}")

        db.close()
        return True

    except Exception as e:
        logger.error(f"❌ Error creating seed data: {e}")
        if "db" in locals():
            db.rollback()
            db.close()
        return False


def clear_seed_data():
    """Clear all seed data"""
    try:
        engine = create_database_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        logger.info("Clearing seed data...")

        # Delete in reverse order of dependencies
        db.query(NewsletterHistory).delete()
        db.query(Newsletter).delete()
        db.query(UserPreferences).delete()
        db.query(User).delete()

        db.commit()
        logger.info("✅ Seed data cleared successfully!")

        db.close()
        return True

    except Exception as e:
        logger.error(f"❌ Error clearing seed data: {e}")
        if "db" in locals():
            db.rollback()
            db.close()
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "create":
            create_seed_data()
        elif command == "clear":
            clear_seed_data()
        else:
            print("Usage: python seed_data.py [create|clear]")
    else:
        create_seed_data()
