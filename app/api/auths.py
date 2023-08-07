import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_versioning import version

from app.config import settings
from app.dependencies import get_auths_service, get_current_user
from app.logger import logger
from app.models.users import Users
from app.schemas.users import SToken, SUserRegister, SUserResponse
from app.services.auths import AuthsService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=SUserResponse, status_code=status.HTTP_201_CREATED)
@version(1)
async def register_user(
    user_data: SUserRegister,
    tasks_service: Annotated[AuthsService, Depends(get_auths_service)],
):
    """Register a new user"""
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
        str(tokens.refresh_token),
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True
    )
    logger.info("Successfully logged in", extra={"id": user.id, "email": user.email})
    return user


@router.post("/logout")
@version(1)
async def logout_user(
    request: Request,
    response: Response,
    tasks_service: Annotated[AuthsService, Depends(get_auths_service)]
) -> dict:
    """Logout an existing user"""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    await tasks_service.logout_user(uuid.UUID(request.cookies.get("refresh_token")))
    logger.info("Successfully logged out")
    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    tasks_service: Annotated[AuthsService, Depends(get_auths_service)]
) -> SToken:
    new_tokens = await tasks_service.refresh_token(
        uuid.UUID(request.cookies.get("refresh_token"))
    )
    response.set_cookie(
        "access_token",
        new_tokens.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True
    )
    response.set_cookie(
        "refresh_token",
        str(new_tokens.refresh_token),
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True
    )
    logger.info("Successfully refresh tokens")
    return new_tokens


@router.post("/abort")
async def abort_all_sessions(
    response: Response,
    tasks_service: Annotated[AuthsService, Depends(get_auths_service)],
    user: Users = Depends(get_current_user)
):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    await tasks_service.abort_all_sessions(user_id=user.id)
    logger.info("Successfully aborted all sessions", extra={"id": user.id, "email": user.email})
    return {"message": "All sessions was aborted"}
