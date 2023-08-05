from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi_versioning import version

from app.api.dependencies import get_users_service
from app.logger import logger
from app.schemas.users import SUserLogin, SUserRegister, SUserResponse
from app.services.users import UsersService


router = APIRouter(prefix="/auth", tags=["Auth"])