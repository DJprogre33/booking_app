from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from fastapi_versioning import version

from app.dependencies import get_current_superuser, get_current_user, get_users_service
from app.logger import logger
from app.models.users import Users
from app.schemas.users import SUserResponse, SUserUpdate
from app.services.users import UsersService

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


@router.put("/me", response_model=SUserResponse)
@version(1)
async def update_me(
    user_data: SUserUpdate,
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
    current_user: Users = Depends(get_current_user)
):
    """Returns the current updated user"""
    updated_user = await tasks_service.update_me(
        user_id=current_user.id,
        email=user_data.email,
        password=user_data.password
    )
    logger.info(
        "Succesfully updated user",
        extra={"user_id": updated_user.id, "user_email": updated_user.email},
    )
    return updated_user


@router.delete("/me", response_model=SUserResponse)
@version(1)
async def delete_me(
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
    current_user: Users = Depends(get_current_user)
):
    """Deletes the user account"""
    deleted_user = await tasks_service.delete_me(current_user.id)
    logger.info(
        "Succesfully deleted user",
        extra={"user_id": deleted_user.id},
    )
    return deleted_user


@router.get("/{user_id}", response_model=SUserResponse)
async def update_user_from_superuser(
    user_id: int,
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
    current_user: Users = Depends(get_current_user)
):
    """Returns user by id"""
    user = await tasks_service.get_user(user_id)
    logger.info(
        "Succesfully got user",
        extra={"user_id": user.id, "user_email": user.email},
    )
    return user


@router.put("/{user_id}", response_model=SUserResponse)
async def update_user_from_superuser(
    user_data: SUserUpdate,
    user_id: int,
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
    current_user: Users = Depends(get_current_superuser)
):
    """Update user by id, current user must have super permissions"""
    user = await tasks_service.update_user_from_superuser(
        user_id=user_id,
        password=user_data.password,
        email=user_data.email
    )
    logger.info(
        "Succesfully updated user",
        extra={"user_id": user.id, "user_email": user.email},
    )
    return user


@router.delete("/{user_id}", response_model=SUserResponse)
async def delete_user_from_superuser(
    user_id: int,
    tasks_service: Annotated[UsersService, Depends(get_users_service)],
    current_user: Users = Depends(get_current_superuser)
):
    """Delete user by id, current user must have super permissions"""
    user = await tasks_service.delete_user_from_superuser(user_id)
    logger.info(
        "Succesfully deleted user",
        extra={"user_id": user.id, "user_email": user.email},
    )
    return user
