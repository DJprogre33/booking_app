from datetime import date, datetime, timedelta

from fastapi import Depends, Request
from jose import JWTError, jwt

from app.config import settings
from app.exceptions import (
    AccessDeniedException,
    IncorrectDataRangeException,
    IncorrectHotelIDException,
    IncorrectTokenFormatException,
    InvalidTokenUserIDException,
    TokenAbsentException,
    TokenExpiredException,
)
from app.hotels.dao import HotelDAO
from app.hotels.models import Hotels
from app.logger import logger
from app.users.dao import UsersDAO
from app.users.models import Users


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

    user = await UsersDAO.find_one_or_none(id=int(user_id))
    if not user:
        logger.warning("Invalid token user id")
        raise InvalidTokenUserIDException()

    return user


def validate_data_range(date_from: date, date_to: date) -> tuple:
    booking_period = date_to - date_from

    if date_from < datetime.utcnow().date():
        logger.error(
            "date_from can't be earlier then now",
            extra={"date_from": date_from, "date_to": date_to},
        )
        raise IncorrectDataRangeException()

    if booking_period < timedelta(days=1) or booking_period > timedelta(days=90):
        logger.error(
            "Incorrect data range", extra={"date_from": date_from, "date_to": date_to}
        )
        raise IncorrectDataRangeException()

    return date_from, date_to


async def check_owner(user, hotel_id: int) -> Users:

    hotel = await HotelDAO.find_one_or_none(id=hotel_id)

    if not hotel:
        logger.warning("Incorrect hotel id", extra={"hotel_id": hotel_id})
        raise IncorrectHotelIDException()

    if hotel.owner_id != user.id:
        logger.warning("User isn't an owner", extra={"hotel_id": hotel_id, "user_id": user.id})
        raise AccessDeniedException()

    return hotel
