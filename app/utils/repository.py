from abc import ABC, abstractmethod

from sqlalchemy import delete, insert, select, update

from app.database import async_session_maker
from app.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    def __init__(self, session: AsyncSession):
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_none(self, **filter_by):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, **filter_by):
        raise NotImplementedError

    @abstractmethod
    async def insert_data(self, **data):
        raise NotImplementedError

    @abstractmethod
    async def update_fields_by_id(self, entity_id, **data):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **filter_by):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_one_or_none(self, **filter_by):
        logger.info("The database query begins to generate")
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        logger.info("Database query successfully completed")
        return result.scalars().one_or_none()

    async def find_all(self, **filter_by):
        logger.info("The database query begins to generate")
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        logger.info("Database query successfully completed")
        return result.scalars().all()

    async def insert_data(self, **data):
        logger.info("The database query begins to generate")
        query = insert(self.model).values(**data).returning(self.model)
        result = await self.session.execute(query)
        logger.info("Database query successfully completed")
        return result.scalar()

    async def update_fields_by_id(self, entity_id: int, **data):
        logger.info("The database query begins to generate")
        query = (
            update(self.model)
            .where(self.model.id == entity_id)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        logger.info("Database query successfully completed")
        return result.scalar()

    async def delete(self, **filter_by):
        query = (
            delete(self.model)
            .filter_by(**filter_by)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        logger.info("Database query successfully completed")
        return result.scalar()
