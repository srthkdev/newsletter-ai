"""
Database management utility for Newsletter AI
"""

import sys
import logging
from create_tables import create_all_tables, drop_all_tables, reset_database
from seed_data import create_seed_data, clear_seed_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def show_help():
    """Show available commands"""
    print("""
Newsletter AI Database Manager

Available commands:
  init        - Initialize database (create tables + seed data)
  create      - Create all database tables
  drop        - Drop all database tables
  reset       - Reset database (drop + create tables)
  seed        - Create seed data for testing
  clear       - Clear all seed data
  help        - Show this help message

Usage:
  python db_manager.py <command>
  
Examples:
  python db_manager.py init     # Set up fresh database
  python db_manager.py reset    # Reset and reseed database
  python db_manager.py seed     # Add test data
    """)


def init_database():
    """Initialize database with tables and seed data"""
    logger.info("🚀 Initializing Newsletter AI database...")

    if create_all_tables():
        logger.info("✅ Tables created successfully")

        if create_seed_data():
            logger.info("✅ Seed data created successfully")
            logger.info("🎉 Database initialization complete!")
            return True
        else:
            logger.error("❌ Failed to create seed data")
            return False
    else:
        logger.error("❌ Failed to create tables")
        return False


def reset_and_seed():
    """Reset database and add seed data"""
    logger.info("🔄 Resetting database with seed data...")

    if reset_database():
        logger.info("✅ Database reset successfully")

        if create_seed_data():
            logger.info("✅ Seed data created successfully")
            logger.info("🎉 Database reset complete!")
            return True
        else:
            logger.error("❌ Failed to create seed data")
            return False
    else:
        logger.error("❌ Failed to reset database")
        return False


def main():
    """Main command handler"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    commands = {
        "init": init_database,
        "create": create_all_tables,
        "drop": drop_all_tables,
        "reset": reset_and_seed,
        "seed": create_seed_data,
        "clear": clear_seed_data,
        "help": show_help,
    }

    if command in commands:
        try:
            commands[command]()
        except KeyboardInterrupt:
            logger.info("\n⚠️  Operation cancelled by user")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
    else:
        logger.error(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
