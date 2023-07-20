from fastapi import APIRouter, Depends, Response
from fastapi_versioning import version

from app.dependencies import get_current_user
from app.exceptions import UserAlreadyExistException
from app.logger import logger
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.users.dao import UsersDAO
from app.users.models import Users
from app.users.schemas import SUserAuth, SUserResponce

router = APIRouter(prefix="/auth", tags=["Auth & users"])


@router.post("/register")
@version(1)
async def register_user(user_data: SUserAuth) -> dict:
    existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        logger.warning("User already exists")
        raise UserAlreadyExistException()
    hashed_password = get_password_hash(user_data.password)
    user_id = await UsersDAO.insert_data(
        email=user_data.email, hashed_password=hashed_password, role=user_data.role
    )
    logger.info("User creared", extra={"id": user_id, "email": user_data.email})
    return {"user_id": user_id}


@router.post("/login", response_model=SUserResponce)
@version(1)
async def login_user(user_data: SUserAuth, response: Response):
    user = await authenticate_user(email=user_data.email, password=user_data.password)
    access_token = create_access_token({"sub": str(user.id)})
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
async def read_users_me(current_user: Users = Depends(get_current_user)):
    user = current_user
    logger.info(
        "Succesfully got user", extra={"user_id": user.id, "user_email": user.email}
    )
    return current_user
