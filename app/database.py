from typing import AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Select the database operation mode
if settings.MODE == "TEST":
    database_url = settings.test_database_url
    database_params = {"poolclass": NullPool}
else:
    database_url = settings.database_url
    database_params = {}


engine = create_async_engine(database_url, **database_params)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy tables"""
    pass
