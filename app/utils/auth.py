from typing import Optional

from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext

from app.exceptions import IncorrectTokenFormatException
from app.logger import logger


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """Rewrite the original class to make OAuth2 work with cookies"""
    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                logger.error("Incorrect token format")
                raise IncorrectTokenFormatException
            return None
        return param


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="auth/login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
