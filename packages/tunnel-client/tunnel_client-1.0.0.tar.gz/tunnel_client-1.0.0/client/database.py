from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


engine: AsyncEngine | None = None
async_session: async_sessionmaker[AsyncSession] | None = None


def get_database_url(db_path: str | None) -> str:
    path = db_path or os.getenv("CLIENT_DB_PATH", "./client.db")
    return f"sqlite+aiosqlite:///{os.path.abspath(path)}"


async def init_engine(db_path: str | None = None) -> AsyncEngine:
    global engine, async_session
    database_url = get_database_url(db_path)
    engine = create_async_engine(database_url, future=True, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    return engine


async def init_db(db_path: str | None = None) -> None:
    from . import models  # noqa
    eng = await init_engine(db_path)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migrate: add new columns to settings table if they don't exist
        await migrate_settings_table(conn)


async def migrate_settings_table(conn) -> None:
    """Add new columns to settings table if they don't exist."""
    from sqlalchemy import text
    
    # Check if table exists and get columns
    def check_and_migrate(sync_conn):
        cursor = sync_conn.execute(text("PRAGMA table_info(settings)"))
        columns = [row[1] for row in cursor.fetchall()]  # Column name is at index 1
        
        # Add server_url if missing
        if "server_url" not in columns:
            sync_conn.execute(text("ALTER TABLE settings ADD COLUMN server_url VARCHAR"))
        
        # Add local_port if missing
        if "local_port" not in columns:
            sync_conn.execute(text("ALTER TABLE settings ADD COLUMN local_port INTEGER"))
        
        sync_conn.commit()
    
    # Run sync migration in async context
    await conn.run_sync(lambda sync_conn: check_and_migrate(sync_conn))


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if async_session is None:
        raise RuntimeError("Database is not initialized. Call init_db() first.")
    session = async_session()
    try:
        yield session
    finally:
        await session.close()


