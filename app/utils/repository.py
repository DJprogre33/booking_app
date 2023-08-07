from abc import ABC, abstractmethod

from sqlalchemy import delete, insert, select, update

from app.database import async_session_maker
from app.exceptions import IncorrectIDException
from app.logger import logger


class AbstractRepository(ABC):

    @classmethod
    @abstractmethod
    async def find_one_or_none(cls, **filter_by):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def find_all(cls, **filter_by):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def insert_data(cls, **data):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def update_fields_by_id(cls, entity_id, **data):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **filter_by):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            logger.info("The database query begins to generate")
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            logger.info("Database query successfully completed")
            return result.scalars().one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            logger.info("The database query begins to generate")
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            logger.info("Database query successfully completed")
            return result.scalars().all()

    @classmethod
    async def insert_data(cls, **data):
        async with async_session_maker() as session:
            logger.info("The database query begins to generate")
            query = insert(cls.model).values(**data).returning(cls.model)
            entity_id = await session.execute(query)
            await session.commit()
            logger.info("Database query successfully completed")
            return entity_id.scalar()

    @classmethod
    async def update_fields_by_id(cls, entity_id: int, **data):
        async with async_session_maker() as session:
            logger.info("The database query begins to generate")
            query = (
                update(cls.model)
                .where(cls.model.id == entity_id)
                .values(**data)
                .returning(cls.model)
            )
            result = await session.execute(query)
            await session.commit()
            logger.info("Database query successfully completed")
            return result.scalar()

    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:
            query = (
                delete(cls.model)
                .filter_by(**filter_by)
                .returning(cls.model)
            )
            result = await session.execute(query)
            await session.commit()
            logger.info("Database query successfully completed")
            return result.scalar()
