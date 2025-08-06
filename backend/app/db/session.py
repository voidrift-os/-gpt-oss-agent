"""Database session utilities."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


# Create the SQLAlchemy async engine using the configured database URL.
engine = create_async_engine(str(settings.database_url), echo=settings.debug)

# Factory for new AsyncSession objects.
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Alias maintained for backwards compatibility with modules that expect
# `SessionLocal`.
SessionLocal = AsyncSessionLocal


async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a new ``AsyncSession`` instance."""
    async with AsyncSessionLocal() as session:
        yield session

