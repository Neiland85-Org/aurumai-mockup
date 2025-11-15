
"""
PostgreSQL Database Configuration with TimescaleDB support
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
from infrastructure.config.settings import settings

# Create async engine
engine = create_async_engine(
    settings.async_database_url,
    echo=False,  # Set to True for SQL query logging
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    Used with FastAPI Depends().
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_database():
    """
    Initialize database tables and TimescaleDB hypertables.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Enable TimescaleDB extension and create hypertables
        # for time-series data
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))

        # Convert raw_measurements to hypertable
        await conn.execute(text(
            """
            SELECT create_hypertable(
                'raw_measurements',
                'timestamp',
                if_not_exists => TRUE
            );
            """
        ))

        # Convert predictions to hypertable
        await conn.execute(text(
            """
            SELECT create_hypertable(
                'predictions',
                'timestamp',
                if_not_exists => TRUE
            );
            """
        ))

        # Convert esg_records to hypertable
        await conn.execute(text(
            """
            SELECT create_hypertable(
                'esg_records',
                'timestamp',
                if_not_exists => TRUE
            );
            """
        ))
