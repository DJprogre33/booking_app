from fastapi import Request

from app.auth.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from app.exceptions import UserAlreadyExistException
from app.logger import logger
from app.models.users import Users
from app.repositories.users import UsersRepository
from app.schemas.users import SUserLogin, SUserRegister


class UsersService:
    def __init__(self, tasks_repo: UsersRepository()):
        self.tasks_repo: UsersRepository = tasks_repo()

    async def register_user(self, user_data: SUserRegister):
        existing_user = await self.tasks_repo.find_one_or_none(email=user_data.email)

        if existing_user:
            logger.warning("User already exists")
            raise UserAlreadyExistException()

        hashed_password = get_password_hash(user_data.password)

        return await self.tasks_repo.insert_data(
            email=user_data.email, hashed_password=hashed_password, role=user_data.role
        )

    async def login_user(self, user_data: SUserLogin):
        existing_user = await self.tasks_repo.find_one_or_none(email=user_data.email)
        user = authenticate_user(
            existing_user=existing_user, password=user_data.password
        )
        return create_access_token({"sub": str(user.id)}), user

    @staticmethod
    async def return_me(request: Request) -> Users:
        user = await get_current_user(request)
        return user

    async def delete_me(self, request: Request) -> int:
        user = await get_current_user(request)
        return await self.tasks_repo.delete_by_id(user.id)
