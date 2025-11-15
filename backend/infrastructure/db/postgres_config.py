"""
PostgreSQL Database Configuration with TimescaleDB support
"""

from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

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


class Base(DeclarativeBase):
    """Typed Declarative base for SQLAlchemy models."""

    pass


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


async def init_database() -> None:
    """
    Initialize database - verify TimescaleDB extension.
    
    IMPORTANT: This function NO LONGER creates tables automatically.
    Use Alembic migrations instead:
    
    1. Create migration: alembic revision --autogenerate -m "description"
    2. Apply migration: alembic upgrade head
    3. Rollback: alembic downgrade -1
    
    This function only ensures TimescaleDB extension is available.
    Table creation and hypertable conversion are handled by migrations.
    """
    async with engine.begin() as conn:
        # Only enable TimescaleDB extension (idempotent operation)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
        
        # NOTE: Table creation removed - use Alembic migrations
        # Tables and hypertables are created via:
        #   alembic upgrade head
        # 
        # This prevents accidental data loss from recreating tables.
        # See: backend/alembic/versions/ for migration files
