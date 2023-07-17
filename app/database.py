from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import NullPool

from app.config import settings


if settings.MODE == "TEST":
    database_url = settings.test_database_url
    database_params = {"poolclass": NullPool}
else:
    database_url = settings.database_url
    database_params = {}

engine = create_async_engine(database_url, **database_params)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass




