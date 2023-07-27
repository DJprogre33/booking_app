from typing import Optional

from pydantic import BaseModel, field_validator


class SRooms(BaseModel):
    name: str
    description: str
    price: int
    services: list
    quantity: int

    @field_validator("price", "quantity")
    @classmethod
    def check_correct_value(cls, value):
        if value <= 0:
            raise ValueError("field must be greater than 0")
        return value


class SRoomResponce(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: Optional[str]
    price: int
    services: list
    quantity: int
    image_path: Optional[str]


class SRoomsResponse(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: Optional[str]
    services: list
    price: int
    quantity: int
    image_path: Optional[str]
    total_cost: int
    rooms_left: int
