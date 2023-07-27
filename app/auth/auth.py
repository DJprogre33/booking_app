from datetime import datetime, timedelta

from fastapi import Request
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.exceptions import (
    IncorrectEmailOrPasswordException,
    IncorrectTokenFormatException,
    InvalidTokenUserIDException,
    TokenAbsentException,
    TokenExpiredException,
)
from app.logger import logger
from app.models.users import Users
from app.repositories.users import UsersRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> str:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, settings.HASHING_ALGORITHM
    )
    return encoded_jwt


def authenticate_user(existing_user: Users, password: str) -> Users:
    if existing_user:
        password_is_valid = verify_password(password, existing_user.hashed_password)
        if password_is_valid:
            return existing_user
    logger.warning("Incorrect email or password")
    raise IncorrectEmailOrPasswordException()


def get_token(request: Request) -> str:
    token = request.cookies.get("booking_access_token")
    if not token:
        logger.warning("Token absent")
        raise TokenAbsentException()
    return token


async def get_current_user(token: str) -> Users:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, settings.HASHING_ALGORITHM)
    except JWTError as exc:
        logger.warning("Incorrect token format")
        raise IncorrectTokenFormatException() from exc

    expire: str = payload.get("exp")
    if not expire or (int(expire) < datetime.utcnow().timestamp()):
        expired_time = datetime.utcfromtimestamp(int(expire))
        logger.warning("Token expired", extra={"expired_time": expired_time})
        raise TokenExpiredException()

    user_id: str = payload.get("sub")
    if not user_id:
        logger.warning("Invalid token user id")
        raise InvalidTokenUserIDException()

    user = await UsersRepository().find_one_or_none(id=int(user_id))
    if not user:
        logger.warning("Invalid token user id")
        raise InvalidTokenUserIDException()

    return user
