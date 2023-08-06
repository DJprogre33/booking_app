import uuid
from typing import Literal

from pydantic import BaseModel, EmailStr


class SUserRegister(BaseModel):
    email: EmailStr
    password: str
    role: Literal["user", "hotel owner"]


class SUserLogin(BaseModel):
    email: EmailStr
    password: str


class SUserResponse(BaseModel):
    id: int
    email: EmailStr
    role: Literal["user", "hotel owner", "admin"]


class Token(BaseModel):
    access_token: str
    refresh_token: uuid.UUID
    token_type: str
