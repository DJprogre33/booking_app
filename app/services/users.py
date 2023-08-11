from typing import Optional

from pydantic import EmailStr

from app.exceptions import IncorrectIDException
from app.logger import logger
from app.models.users import Users
from app.utils.auth import get_password_hash
from app.utils.transaction_manager import ITransactionManager


class UsersService:

    @staticmethod
    async def get_users_list(
        transaction_manager: ITransactionManager,
        offset: int,
        limit: int
    ) -> Optional[list[Users]]:
        async with transaction_manager:
            users = await transaction_manager.users.get_users_list(offset=offset, limit=limit)
            await transaction_manager.commit()
            return users

    @staticmethod
    async def return_me(transaction_manager: ITransactionManager, user_id: int) -> Users:
        async with transaction_manager:
            user = await transaction_manager.users.find_one_or_none(id=user_id)
            await transaction_manager.commit()
            return user

    @staticmethod
    async def update_me(
        transaction_manager: ITransactionManager,
        user_id: int,
        email: EmailStr,
        password: str
    ) -> Users:
        hashed_password = get_password_hash(password)
        async with transaction_manager:
            updated_user = await transaction_manager.users.update_fields_by_id(
                entity_id=user_id,
                email=email,
                hashed_password=hashed_password
            )
            await transaction_manager.commit()
            return updated_user

    @staticmethod
    async def delete_me(transaction_manager: ITransactionManager, user_id: int) -> Users:
        async with transaction_manager:
            deleted_user = await transaction_manager.users.delete(id=user_id)
            await transaction_manager.commit()
            return deleted_user

    @staticmethod
    async def get_user(transaction_manager: ITransactionManager, user_id: int) -> Users:
        async with transaction_manager:
            user = await transaction_manager.users.find_one_or_none(id=user_id)
            if not user:
                raise IncorrectIDException
            await transaction_manager.commit()
            return user

    @staticmethod
    async def update_user_from_superuser(
        transaction_manager: ITransactionManager,
        user_id: int,
        password: str,
        email: EmailStr
    ) -> Users:
        async with transaction_manager:
            exists_user = await transaction_manager.users.find_one_or_none(id=user_id)
            if not exists_user:
                logger.warning("Entity id not found", extra={"entity_id": user_id})
                raise IncorrectIDException
            hashed_password = get_password_hash(password)
            updated_user = await transaction_manager.users.update_fields_by_id(
                entity_id=user_id,
                hashed_password=hashed_password,
                email=email
            )
            await transaction_manager.commit()
            return updated_user

    @staticmethod
    async def delete_user_from_superuser(transaction_manager: ITransactionManager, user_id: int) -> Users:
        async with transaction_manager:
            exists_user = await transaction_manager.users.find_one_or_none(id=user_id)
            if not exists_user:
                logger.warning("Entity id not found", extra={"entity_id": user_id})
                raise IncorrectIDException
            deleted_user = await transaction_manager.users.delete(id=user_id)
            await transaction_manager.commit()
            return deleted_user
