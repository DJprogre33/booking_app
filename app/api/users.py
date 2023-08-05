from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi_versioning import version

from app.api.dependencies import get_users_service
from app.logger import logger
from app.schemas.users import SUserLogin, SUserRegister, SUserResponse
from app.services.users import UsersService

from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=SUserResponse)
@version(1)
async def register_user(
    user_data: SUserRegister,
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
) -> dict:
    """Registers a new user"""
    user = await tasks_service.register_user(user_data=user_data)

    logger.info("User created", extra={"id": user.id, "email": user.email})

    return user


@router.post("/login", response_model=SUserResponse)
@version(1)
async def login_user(
    response: Response,
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
    credentials: OAuth2PasswordRequestForm = Depends()
):
    """Login an existing user"""
    access_token, user = await tasks_service.login_user(
        credentials.password, credentials.username
    )
    response.set_cookie("access_token", access_token, httponly=True)

    logger.info("Successfully logged in", extra={"id": user.id, "email": user.email})

    return user


@router.post("/logout")
@version(1)
async def logout_user(response: Response) -> None:
    """Logout an existing user"""
    response.delete_cookie("booking_access_token")

    logger.info("Successfully logged out")


@router.get("/me", response_model=SUserResponse)
@version(1)
async def return_me(
    request: Request, tasks_service: Annotated[UsersService, Depends(get_users_service)]
):
    """Returns the current authenticated user"""
    current_user = await tasks_service.return_me(request)

    logger.info(
        "Succesfully got user",
        extra={"user_id": current_user.id, "user_email": current_user.email},
    )

    return current_user


@router.delete("/me")
@version(1)
async def delete_me(
    request: Request, tasks_service: Annotated[UsersService, Depends(get_users_service)]
) -> dict[str, int]:
    """Deletes the user account"""
    deleted_user_id = await tasks_service.delete_me(request)

    logger.info(
        "Succesfully deleted user",
        extra={"user_id": deleted_user_id},
    )

    return {"deleted_user_id": deleted_user_id}
