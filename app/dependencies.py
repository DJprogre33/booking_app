from datetime import datetime

from fastapi import Depends, Request
from jose import JWTError, jwt

from app.config import settings
from app.exceptions import (
    IncorrectTokenFormatException,
    InvalidTokenUserIDException,
    TokenAbsentException,
    TokenExpiredException,
)
from app.logger import logger
from app.models.users import Users
from app.repositories.users import UsersRepository


def get_token(request: Request) -> str:
    token = request.cookies.get("booking_access_token")
    if not token:
        logger.warning("Token absent")
        raise TokenAbsentException()
    return token


async def get_current_user(token: str = Depends(get_token)) -> Users:
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
