from typing import Type

from app.services.bookings import BookingsService
from app.services.hotels import HotelsService
from app.services.rooms import RoomsService
from app.services.users import UsersService
from app.services.auths import AuthsService
from app.utils.auth import oauth2_scheme
from app.models.users import Users
from app.exceptions import IncorrectTokenFormatException, TokenExpiredException, InvalidTokenUserIDException
from app.config import settings
from app.logger import logger
from app.repositories.users import UsersRepository

from fastapi import Depends
from jose import jwt, JWTError
from datetime import datetime

# functions return the service instance
def get_bookings_service() -> Type[BookingsService]:
    return BookingsService


def get_rooms_service() -> Type[RoomsService]:
    return RoomsService


def get_hotels_service() -> Type[HotelsService]:
    return HotelsService


def get_users_service() -> Type[UsersService]:
    return UsersService


def get_auths_service() -> Type[AuthsService]:
    return AuthsService


async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> Users:
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

    user = await UsersRepository.find_one_or_none(id=int(user_id))
    if not user:
        logger.warning("Invalid token user id")
        raise InvalidTokenUserIDException()
    return user


async def get_current_hotel_owner(current_user: Users = Depends(get_current_user)) -> Users:
    pass