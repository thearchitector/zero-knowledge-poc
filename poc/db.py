from contextlib import asynccontextmanager
from functools import cache

import asyncio_atexit
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DB_URL = "postgresql+asyncpg://user:pass@db:5432/db"


@cache
def create_engine(db_url, **kwargs):
    """
    Create and return a new asyncio-backed database engine, merging the provided
    kwargs (if any) with the application defaults.
    """
    engine = create_async_engine(db_url, **kwargs)
    asyncio_atexit.register(engine.dispose)
    return engine


@cache
def create_sessionmaker(db_url, autoflush=True, expire_on_commit=True, **kwargs):
    engine = create_engine(db_url, **kwargs)
    return async_sessionmaker(
        engine, autoflush=autoflush, expire_on_commit=expire_on_commit
    )


@asynccontextmanager
async def create_session():
    session_maker = create_sessionmaker(DB_URL)

    async with session_maker() as session:
        yield session
