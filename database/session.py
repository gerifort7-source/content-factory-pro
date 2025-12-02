"""Database session and connection management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
import logging

from database.models import Base
from core.config import settings

logger = logging.getLogger(__name__)

# Database URL construction
if settings.DATABASE_URL:
    DATABASE_URL = settings.DATABASE_URL
else:
    # SQLite fallback for development
    DATABASE_URL = "sqlite:///./test.db"

logger.info(f"Using database: {DATABASE_URL.split('://')[0]}")

# Create engine with appropriate connection pool
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


def close_db():
    """Close database connection"""
    try:
        engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")
        raise


def get_session() -> Session:
    """Get a new database session"""
    return SessionLocal()


class DatabaseManager:
    """Manager for database operations"""

    def __init__(self):
        """Initialize database manager"""
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.logger = logger

    def create_tables(self):
        """Create all tables in database"""
        try:
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("All tables created successfully")
        except Exception as e:
            self.logger.error(f"Error creating tables: {str(e)}")
            raise

    def drop_tables(self):
        """Drop all tables from database - USE WITH CAUTION"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            self.logger.warning("All tables dropped from database")
        except Exception as e:
            self.logger.error(f"Error dropping tables: {str(e)}")
            raise

    def get_session(self) -> Session:
        """Get a new session"""
        return self.SessionLocal()

    def close(self):
        """Close database connection pool"""
        try:
            self.engine.dispose()
            self.logger.info("Database connection pool closed")
        except Exception as e:
            self.logger.error(f"Error closing database: {str(e)}")
            raise

    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.engine.connect() as conn:
                self.logger.info("Database health check: OK")
                return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {str(e)}")
            return False


# Global instance
db_manager = DatabaseManager()
