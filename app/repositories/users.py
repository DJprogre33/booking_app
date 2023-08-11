from typing import Optional

from sqlalchemy import select

from app.logger import logger
from app.models.users import Users
from app.utils.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = Users

    async def get_users_list(self, offset: int, limit: int) -> Optional[list[Users]]:
        logger.info("The database query begins to generate")
        query = select(self.model).offset(offset).limit(limit)
        users = await self.session.execute(query)
        logger.info("Database query successfully completed")
        return users.scalars().all()
