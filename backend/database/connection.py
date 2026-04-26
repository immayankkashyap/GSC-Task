"""
Database / cache stubs for Task 1.
Full PostgreSQL integration will be added when the DB schema is finalised.
"""
from typing import AsyncGenerator, Optional


async def get_cache(key: str) -> Optional[str]:
    """Returns None (cache miss) until Redis/Postgres cache is wired up."""
    return None


async def get_db() -> AsyncGenerator:
    """
    Async generator yielding a DB session.
    Currently a no-op stub; replace with SQLAlchemy AsyncSession later.
    """
    yield None
