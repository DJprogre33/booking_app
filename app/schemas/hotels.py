from pydantic import BaseModel, field_validator
from typing import Optional


class SHotel(BaseModel):
    name: str
    location: str
    services: list
    rooms_quantity: int

    @field_validator("rooms_quantity")
    @classmethod
    def check_correct_value(cls, value):
        if value <= 0:
            raise ValueError("field must be greater than 0")
        return value


class SHotelResponse(BaseModel):
    id: int
    name: str
    location: str
    services: list
    rooms_quantity: int
    image_path: Optional[str]


class SHotelsResponse(BaseModel):
    id: int
    name: str
    location: str
    services: list
    rooms_quantity: int
    image_path: Optional[str]
    rooms_left: int

