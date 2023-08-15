import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt
from pydantic import EmailStr, ValidationError

from app.config import settings
from app.exceptions import (
    IncorrectCredentials,
    IncorrectEmailOrPasswordException,
    InvalidTokenUserIDException,
    TokenAbsentException,
    TokenExpiredException,
    UserAlreadyExistException,
)
from app.logger import logger
from app.models.users import Users
from app.schemas.users import SToken, SUserLogin
from app.utils.auth import get_password_hash, verify_password
from app.utils.transaction_manager import ITransactionManager


class AuthsService:

    @staticmethod
    async def register_user(
        transaction_manager: ITransactionManager,
        email: EmailStr,
        password: str,
        role: str,
    ) -> Users:
        async with transaction_manager:
            existing_user = await transaction_manager.users.find_one_or_none(
                email=email
            )
            if existing_user:
                logger.warning("User already exists")
                raise UserAlreadyExistException
            hashed_password = get_password_hash(password)
            new_user = await transaction_manager.users.insert_data(
                email=email, hashed_password=hashed_password, role=role
            )
            await transaction_manager.commit()
            return new_user

    async def login_user(
        self, transaction_manager: ITransactionManager, password: str, email: EmailStr
    ) -> tuple[SToken, Users]:
        self._validate_credentials(email=email, password=password)
        async with transaction_manager:
            existing_user = await transaction_manager.users.find_one_or_none(
                email=email
            )
            user = self._authenticate_user(
                existing_user=existing_user, password=password
            )
            access_token = self._create_access_token(user.id)
            refresh_token = self._create_refresh_token()
            refresh_token_expires = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            await transaction_manager.auth.insert_data(
                refresh_token=refresh_token,
                expires_in=refresh_token_expires.total_seconds(),
                user_id=user.id,
            )
            await transaction_manager.commit()
            token = SToken(access_token=access_token, refresh_token=refresh_token)
            return token, user

    @staticmethod
    async def logout_user(transaction_manager: ITransactionManager, token: str) -> None:
        async with transaction_manager:
            refresh_session = await transaction_manager.auth.find_one_or_none(
                refresh_token=token
            )
            if refresh_session:
                await transaction_manager.auth.delete(id=refresh_session.id)
                await transaction_manager.commit()

    async def refresh_token(
        self, transaction_manager: ITransactionManager, token: str
    ) -> SToken:
        async with transaction_manager:
            refresh_session = await transaction_manager.auth.find_one_or_none(
                refresh_token=token
            )
            if refresh_session is None:
                raise TokenAbsentException
            if datetime.now(timezone.utc) >= refresh_session.created_at + timedelta(
                seconds=refresh_session.expires_in
            ):
                await transaction_manager.auth.delete(id=refresh_session.id)
                raise TokenExpiredException

            user = await transaction_manager.users.find_one_or_none(
                id=refresh_session.user_id
            )
            if user is None:
                raise InvalidTokenUserIDException

            access_token = self._create_access_token(user.id)
            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = self._create_refresh_token()

            await transaction_manager.auth.update_fields_by_id(
                refresh_session.id,
                refresh_token=refresh_token,
                expires_in=refresh_token_expires.total_seconds(),
            )
            await transaction_manager.commit()
            return SToken(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    async def abort_all_sessions(
        transaction_manager: ITransactionManager, user_id: int
    ) -> None:
        async with transaction_manager:
            await transaction_manager.auth.delete(user_id=user_id)
            await transaction_manager.commit()

    @staticmethod
    def _authenticate_user(existing_user: Users, password: str) -> Users:
        if existing_user:
            password_is_valid = verify_password(password, existing_user.hashed_password)
            if password_is_valid:
                return existing_user
        logger.warning("Incorrect email or password")
        raise IncorrectEmailOrPasswordException

    @staticmethod
    def _create_access_token(user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"sub": str(user_id), "exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, settings.HASHING_ALGORITHM
        )
        return f"Bearer {encoded_jwt}"

    @staticmethod
    def _create_refresh_token() -> uuid.UUID:
        return uuid.uuid4()

    @staticmethod
    def _validate_credentials(email: EmailStr, password: str) -> None:
        try:
            SUserLogin(email=email, password=password)
        except ValidationError as err:
            raise IncorrectCredentials from err
