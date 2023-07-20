from typing import Union

from sqlalchemy import insert, select, update

from app.database import async_session_maker


class BaseDAO:
    """
    Basic DAO class that contains common methods for all Sqlalchemy models
    """

    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def insert_data(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model.id)
            entity_id = await session.execute(query)
            await session.commit()
            return entity_id.scalar()

    @classmethod
    async def update_fields_by_id(cls, entity_id, **data):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.id == entity_id).values(**data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalar()