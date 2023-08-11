from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_versioning import version

from app.config import settings
from app.dependencies import TManagerDep, get_current_user
from app.exceptions import SExstraResponse
from app.logger import logger
from app.models.users import Users
from app.schemas.users import SToken, SUserRegister, SUserResponse
from app.services.auths import AuthsService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=SUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": SExstraResponse}
    }
)
@version(1)
async def register_user(
    user_data: SUserRegister,
    transaction_manager: TManagerDep
):
    """Register a new user"""
    new_user = await AuthsService().register_user(
        transaction_manager=transaction_manager,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role
    )
    logger.info("User created", extra={"id": new_user.id, "email": new_user.email})
    return new_user


@router.post(
    "/login",
    response_model=SUserResponse,
    responses={
        401: {"model": SExstraResponse}
    }
)
@version(1)
async def login_user(
    response: Response,
    transaction_manager: TManagerDep,
    credentials: OAuth2PasswordRequestForm = Depends()
):
    """Login an existing user"""
    tokens, user = await AuthsService().login_user(
        transaction_manager=transaction_manager,
        password=credentials.password,
        email=credentials.username
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
    transaction_manager: TManagerDep
) -> dict:
    """Logout an existing user"""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    await AuthsService().logout_user(
        transaction_manager=transaction_manager,
        token=request.cookies.get("refresh_token")
    )
    logger.info("Successfully logged out")
    return {"message": "Successfully logged out"}


@router.post(
    "/refresh",
    response_model=SToken,
    responses={
        401: {"model": SExstraResponse}
    }
)
@version(1)
async def refresh_token(
    request: Request,
    response: Response,
    transaction_manager: TManagerDep
):
    new_tokens = await AuthsService().refresh_token(
        transaction_manager=transaction_manager,
        token=request.cookies.get("refresh_token")
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


@router.post(
    "/abort",
    responses={
        401: {"model": SExstraResponse}
    }
)
@version(1)
async def abort_all_sessions(
    response: Response,
    transaction_manager: TManagerDep,
    user: Users = Depends(get_current_user)
) -> dict:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    await AuthsService().abort_all_sessions(
        transaction_manager=transaction_manager,
        user_id=user.id
    )
    logger.info("Successfully aborted all sessions", extra={"id": user.id, "email": user.email})
    return {"message": "All sessions was aborted"}
