from pydantic import BaseModel, field_validator


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
    name: str
    location: str
    rooms_quantity: int
    image_path: str
    id: int
    services: list


class SHotelsResponse(BaseModel):
    id: int
    name: str
    location: str
    services: list
    rooms_quantity: int
    image_path: str
    rooms_left: int

