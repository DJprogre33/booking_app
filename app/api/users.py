from typing import Annotated

from fastapi import APIRouter, Depends, Response, Request
from fastapi_versioning import version

from app.api.dependencies import get_users_service
from app.logger import logger
from app.schemas.users import SUserAuth, SUserResponce
from app.services.users import UsersService

router = APIRouter(prefix="/auth", tags=["Auth & users"])


@router.post("/register")
@version(1)
async def register_user(
    user_data: SUserAuth,
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
) -> dict:
    user_id = await tasks_service.register_user(user_data=user_data)

    logger.info("User created", extra={"id": user_id, "email": user_data.email})

    return {"user_id": user_id}


@router.post("/login", response_model=SUserResponce)
@version(1)
async def login_user(
    user_data: SUserAuth,
    response: Response,
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
):
    access_token, user = await tasks_service.login_user(user_data=user_data)
    response.set_cookie("booking_access_token", access_token, httponly=True)

    logger.info("Successfully logged in", extra={"id": user.id, "email": user.email})

    return user


@router.post("/logout")
@version(1)
async def logout_user(response: Response):
    response.delete_cookie("booking_access_token")

    logger.info("Successfully logged out")


@router.get("/me", response_model=SUserResponce)
@version(1)
async def return_me(
    request: Request,
    tasks_service: Annotated[UsersService, Depends(get_users_service)]
):
    current_user = await tasks_service.return_me(request)

    logger.info(
        "Succesfully got user",
        extra={"user_id": current_user.id, "user_email": current_user.email},
    )

    return current_user


@router.delete("/me", response_model=SUserResponce)
@version(1)
async def delete_me(
    request: Request,
    tasks_service: Annotated[UsersService, Depends(get_users_service)]
):
    deleted_user = await tasks_service.delete_me(request)

    logger.info(
        "Succesfully deleted user",
        extra={"user_id": deleted_user.id, "user_email": deleted_user.email},
    )

    return deleted_user
