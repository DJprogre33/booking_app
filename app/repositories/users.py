from app.models.users import Users
from app.utils.repository import SQLAlchemyRepository
from app.database import async_session_maker
from sqlalchemy import select
from app.logger import logger
from typing import Optional

class UsersRepository(SQLAlchemyRepository):
    model = Users

    @classmethod
    async def get_users_list(cls, offset: int, limit: int) -> Optional[list[Users]]:
        async with async_session_maker() as session:
            logger.info("The database query begins to generate")
            query = select(cls.model).offset(offset).limit(limit)
            users = await session.execute(query)
            logger.info("Database query successfully completed")
            return users.scalars().all()
