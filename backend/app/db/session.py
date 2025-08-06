"""Database session utilities."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


# Create the SQLAlchemy async engine using the configured database URL.
# ``echo`` is controlled by ``settings.debug`` for optional SQL logging but
# safely falls back to ``False`` when the attribute is missing.
engine = create_async_engine(
    str(settings.database_url),
    echo=getattr(settings, "debug", False),
)

# Factory for new AsyncSession objects.
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Alias maintained for backwards compatibility with modules that expect
# `SessionLocal`.
SessionLocal = AsyncSessionLocal


async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a new ``AsyncSession`` instance."""
    async with AsyncSessionLocal() as session:
        yield session

