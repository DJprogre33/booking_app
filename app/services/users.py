from fastapi import Request
from typing import Optional


from app.exceptions import UserAlreadyExistException
from app.logger import logger
from app.models.users import Users
from app.repositories.users import UsersRepository
from app.schemas.users import SToken, SUserRegister
from pydantic import EmailStr

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
    #
    # @classmethod
    # async def delete_me(cls, request: Request) -> int:
    #     token = get_token(request)
    #     user = await get_current_user(token)
    #     return await cls.tasks_repo.delete(id=user.id)
