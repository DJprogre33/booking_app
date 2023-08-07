from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi_versioning import version

from app.dependencies import get_users_service
from app.logger import logger
from app.schemas.users import SUserResponse
from app.services.users import UsersService

router = APIRouter(prefix="/users", tags=["Users"])


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
