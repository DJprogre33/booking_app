from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi_versioning import version
from app.config import settings
from app.api.dependencies import get_auths_service
from app.logger import logger
from app.schemas.users import SUserLogin, SUserRegister, SUserResponse
from app.services.auths import AuthsService
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=SUserResponse, status_code=status.HTTP_201_CREATED)
@version(1)
async def register_user(
    user_data: SUserRegister,
    tasks_service: Annotated[AuthsService, Depends(get_auths_service)],
) -> SUserResponse:
    """Registers a new user"""
    user = await tasks_service.register_user(user_data=user_data)
    logger.info("User created", extra={"id": user.id, "email": user.email})
    return user


@router.post("/login", response_model=SUserResponse)
@version(1)
async def login_user(
    response: Response,
    tasks_service: Annotated[AuthsService, Depends(get_auths_service)],
    credentials: OAuth2PasswordRequestForm = Depends()
):
    """Login an existing user"""
    tokens, user = await tasks_service.login_user(
        credentials.password, credentials.username
    )
    response.set_cookie(
        "access_token",
        tokens.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True
    )
    response.set_cookie(
        "refresh_token",
        tokens.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True
    )
    logger.info("Successfully logged in", extra={"id": user.id, "email": user.email})
    return user


@router.post("/logout")
@version(1)
async def logout_user(response: Response) -> None:
    """Logout an existing user"""
    response.delete_cookie("booking_access_token")

    logger.info("Successfully logged out")