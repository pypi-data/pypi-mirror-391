"""Database connection and session management."""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from ..core.config import get_settings

logger = logging.getLogger(__name__)

# Global variables
engine = None
SessionLocal = None
Base = declarative_base()


def get_database_url() -> str:
    """Get database URL from settings."""
    settings = get_settings()
    return settings.database_url


def create_database_engine():
    """Create database engine."""
    global engine
    
    database_url = get_database_url()
    
    # Configure engine based on database type
    if database_url.startswith("sqlite"):
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    else:
        engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )
    
    logger.info(f"Database engine created: {database_url}")
    return engine


def get_session_factory():
    """Get session factory."""
    global SessionLocal
    
    if SessionLocal is None:
        if engine is None:
            create_database_engine()
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal


def get_database() -> Generator[Session, None, None]:
    """Get database session."""
    session_factory = get_session_factory()
    session = session_factory()
    
    try:
        yield session
    finally:
        session.close()


def init_database() -> None:
    """Initialize database tables."""
    global engine, Base
    
    if engine is None:
        create_database_engine()
    
    # Import all models to ensure they are registered
    from . import models
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_database() -> None:
    """Drop all database tables."""
    global engine, Base
    
    if engine is None:
        create_database_engine()
    
    # Import all models to ensure they are registered
    from . import models
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped successfully")


def reset_database() -> None:
    """Reset database (drop and recreate all tables)."""
    drop_database()
    init_database()
    logger.info("Database reset successfully")
