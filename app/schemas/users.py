from typing import Literal

from pydantic import BaseModel, EmailStr


class SUserAuth(BaseModel):
    email: EmailStr
    password: str
    role: Literal["user", "hotel owner"]


class SUserResponce(BaseModel):
    id: int
    email: EmailStr
    role: Literal["user", "hotel owner", "admin"]


