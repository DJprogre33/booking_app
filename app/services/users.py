from typing import Optional

from app.exceptions import IncorrectIDException
from app.logger import logger
from app.models.users import Users
from app.repositories.users import UsersRepository
from pydantic import EmailStr
from app.utils.auth import get_password_hash


class UsersService:
    tasks_repo: UsersRepository = UsersRepository

    @classmethod
    async def get_users_list(cls, offset: int, limit: int) -> Optional[list[Users]]:
        users = await cls.tasks_repo.get_users_list(offset=offset, limit=limit)
        return users

    @classmethod
    async def return_me(cls, user_id: int) -> Users:
        user = await cls.tasks_repo.find_one_or_none(id=user_id)
        return user

    @classmethod
    async def update_me(cls, user_id: int, email: EmailStr, password: str) -> Users:
        hashed_password = get_password_hash(password)
        user = await cls.tasks_repo.update_fields_by_id(
            entity_id=user_id,
            email=email,
            hashed_password=hashed_password
        )
        return user

    @classmethod
    async def delete_me(cls, user_id: int) -> Users:
        return await cls.tasks_repo.delete(id=user_id)

    @classmethod
    async def get_user(cls, user_id: int) -> Users:
        user = await cls.tasks_repo.find_one_or_none(id=user_id)
        if not user:
            raise IncorrectIDException
        return user

    @classmethod
    async def update_user_from_superuser(
        cls,
        user_id: int,
        password: str,
        email: EmailStr
    ) -> Users:
        exists_user = await cls.tasks_repo.find_one_or_none(id=user_id)
        if not exists_user:
            logger.warning("Entity id not found", extra={"entity_id": user_id})
            raise IncorrectIDException
        hashed_password = get_password_hash(password)
        user = await cls.tasks_repo.update_fields_by_id(
            entity_id=user_id,
            hashed_password=hashed_password,
            email=email
        )
        return user

    @classmethod
    async def delete_user_from_superuser(cls, user_id: int) -> Users:
        exists_user = await cls.tasks_repo.find_one_or_none(id=user_id)
        if not exists_user:
            logger.warning("Entity id not found", extra={"entity_id": user_id})
            raise IncorrectIDException
        user = await cls.tasks_repo.delete(id=user_id)
        return user
