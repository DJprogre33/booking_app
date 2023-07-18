from fastapi import Request, Depends
from jose import jwt, JWTError
from app.config import settings
from datetime import datetime, date, timedelta
from app.users.dao import UsersDAO
from app.users.models import Users
from app.exceptions import (
    TokenExpiredException, TokenAbsentException, IncorrectTokenFormatException,
    InvalidTokenUserIException, IncorrectDataRangeException
)


def get_token(request: Request) -> str:
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException()
    return token


async def get_current_user(token: str = Depends(get_token)) -> Users:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            settings.HASHING_ALGORITHM
        )
    except JWTError:
        raise IncorrectTokenFormatException()

    expire: str = payload.get("exp")
    if not expire or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpiredException()

    user_id: str = payload.get("sub")
    if not user_id:
        raise InvalidTokenUserIException()
    user = await UsersDAO.find_one_or_none(id=int(user_id))
    if not user:
        raise InvalidTokenUserIException()
    return user


def validate_data_range(date_from: date, date_to: date) -> tuple:
    booking_period = date_to - date_from
    if booking_period < timedelta(days=1) or booking_period > timedelta(days=90):
        raise IncorrectDataRangeException()
    return date_from, date_to
