from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update

from app.database import async_session_maker


class AbstractRepository(ABC):
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


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def find_one_or_none(self, **filter_by):
        async with async_session_maker() as session:
            query = select(self.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    async def find_all(self, **filter_by):
        async with async_session_maker() as session:
            query = select(self.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    async def insert_data(self, **data):
        async with async_session_maker() as session:
            query = insert(self.model).values(**data).returning(self.model.id)
            entity_id = await session.execute(query)
            await session.commit()
            return entity_id.scalar()

    async def update_fields_by_id(self, entity_id, **data):
        async with async_session_maker() as session:
            query = (
                update(self.model)
                .where(self.model.id == entity_id)
                .values(**data)
                .returning(self.model)
            )
            result = await session.execute(query)
            await session.commit()
            return result.scalar()
