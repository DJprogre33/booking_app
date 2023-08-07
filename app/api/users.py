from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from fastapi_versioning import version

from app.dependencies import get_users_service
from app.logger import logger
from app.schemas.users import SUserResponse
from app.services.users import UsersService
from app.dependencies import get_current_superuser, get_current_user
from app.models.users import Users


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=Optional[list[SUserResponse]])
async def get_users_list(
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
    current_user: Users = Depends(get_current_superuser),
    offset: Optional[int] = 0,
    limit: Optional[int] = 50
):
    """Returns registered users with pagination, current user must have super permissions"""
    users = await tasks_service.get_users_list(offset=offset, limit=limit)
    logger.info("Successfully got users list", extra={"total_users": len(users) if users else 0})
    return users


@router.get("/me", response_model=SUserResponse)
@version(1)
async def return_me(
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
    current_user: Users = Depends(get_current_user)
):
    """Returns the current authenticated user"""
    current_user = await tasks_service.return_me(current_user.id)
    logger.info(
        "Succesfully got user",
        extra={"user_id": current_user.id, "user_email": current_user.email},
    )
    return current_user
#
#
# @router.delete("/me")
# @version(1)
# async def delete_me(
#     request: Request, tasks_service: Annotated[UsersService, Depends(get_users_service)]
# ) -> dict[str, int]:
#     """Deletes the user account"""
#     deleted_user_id = await tasks_service.delete_me(request)
#
#     logger.info(
#         "Succesfully deleted user",
#         extra={"user_id": deleted_user_id},
#     )
#
#     return {"deleted_user_id": deleted_user_id}
