from fastapi import Request
from typing import Optional, Tuple, Type

from app.utils.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    get_token,
    verify_password
)
from app.exceptions import UserAlreadyExistException, IncorrectEmailOrPasswordException
from app.logger import logger
from app.models.users import Users
from app.repositories.users import UsersRepository
from app.repositories.auths import AuthsRepository
from app.schemas.users import Token, SUserRegister
from pydantic import EmailStr


class AuthsService:
    tasks_repo: UsersRepository = AuthsRepository
    @classmethod
    def _authenticate_user(cls, existing_user: Users, password: str) -> Users:
        if existing_user:
            password_is_valid = verify_password(password, existing_user.hashed_password)
            if password_is_valid:
                return existing_user
        logger.warning("Incorrect email or password")
        raise IncorrectEmailOrPasswordException()

    @classmethod
    def _create_access_token(cls):
        pass

    @classmethod
    def _create_refresh_token(cls):
        pass

    @classmethod
    async def register_user(cls, user_data: SUserRegister) -> Users:
        existing_user = await cls.tasks_repo.find_one_or_none(email=user_data.email)
        if existing_user:
            logger.warning("User already exists")
            raise UserAlreadyExistException()
        hashed_password = get_password_hash(user_data.password)
        return await cls.tasks_repo.insert_data(
            email=user_data.email, hashed_password=hashed_password, role=user_data.role
        )

    @classmethod
    async def login_user(cls, password: str, email: EmailStr) -> tuple[Token, Users]:
        existing_user = await cls.tasks_repo.find_one_or_none(email=email)
        user = cls._authenticate_user(
            existing_user=existing_user, password=password
        )
        access_token = await cls._create_access_token()
        refresh_token = await cls._create_refresh_token()
        token = Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

        return token, user
