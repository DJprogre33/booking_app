from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from pydantic import EmailStr
from app.users.dao import UsersDAO
from app.users.models import Users
from app.config import settings
from app.exceptions import IncorrectEmailOrPasswordException


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
        to_encode,
        settings.JWT_SECRET_KEY,
        settings.HASHING_ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str) -> Users:
    existing_user = await UsersDAO.find_one_or_none(email=email)

    if existing_user:
        password_is_valid = verify_password(password, existing_user.hashed_password)
        if password_is_valid:
            return existing_user
    raise IncorrectEmailOrPasswordException()
