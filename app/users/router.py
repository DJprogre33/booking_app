from fastapi import APIRouter, Depends, Response

from app.dependencies import get_current_user
from app.exceptions import UserAlreadyExistException
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.users.dao import UsersDAO
from app.users.models import Users
from app.users.schemas import SUserAuth

router = APIRouter(
    prefix="/auth",
    tags=["Auth & users"]
)


@router.post("/register")
async def register_user(user_data: SUserAuth):
    existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistException()
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.insert_data(
        email=user_data.email,
        hashed_password=hashed_password
    )


@router.post("/login")
async def login_user(user_data: SUserAuth, response: Response):
    user = await authenticate_user(
        email=user_data.email,
        password=user_data.password
    )
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("booking_access_token", access_token, httponly=True)
    return access_token


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("booking_access_token")


@router.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user
