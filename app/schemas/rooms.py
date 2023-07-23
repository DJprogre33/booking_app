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


class SRoomsResponse(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    services: list
    price: int
    quantity: int
    image_id: int
    total_cost: int
    rooms_left: int
