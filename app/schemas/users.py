from typing import Literal

from pydantic import BaseModel, EmailStr


class SUserRegister(BaseModel):
    email: EmailStr
    password: str
    role: Literal["user", "hotel owner"]


class SUserLogin(BaseModel):
    email: EmailStr
    password: str


class SUserResponce(BaseModel):
    id: int
    email: EmailStr
    role: Literal["user", "hotel owner", "admin"]


