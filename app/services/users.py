from fastapi import Request
from typing import Optional

from app.auth.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    get_token,
)
from app.exceptions import UserAlreadyExistException
from app.logger import logger
from app.models.users import Users
from app.repositories.users import UsersRepository
from app.schemas.users import SToken, SUserRegister
from pydantic import EmailStr

class UsersService:
    tasks_repo: UsersRepository = UsersRepository
    
    @classmethod
    async def register_user(cls, user_data: SUserRegister) -> Optional[Users]:
        existing_user = await cls.tasks_repo.find_one_or_none(email=user_data.email)
        if existing_user:
            logger.warning("User already exists")
            raise UserAlreadyExistException()
        hashed_password = get_password_hash(user_data.password)
        return await cls.tasks_repo.insert_data(
            email=user_data.email, hashed_password=hashed_password, role=user_data.role
        )
    
    @classmethod
    async def login_user(cls, password: str, email: EmailStr) -> Optional[tuple[str, Users]]:
        existing_user = await cls.tasks_repo.find_one_or_none(email=email)
        user = authenticate_user(
            existing_user=existing_user, password=password
        )
        return create_access_token({"sub": str(user.id)}), user

    @staticmethod
    async def return_me(request: Request) -> Users:
        token = get_token(request)
        user = await get_current_user(token)
        return user
    
    @classmethod
    async def delete_me(cls, request: Request) -> int:
        token = get_token(request)
        user = await get_current_user(token)
        return await cls.tasks_repo.delete_by_id(user.id)
