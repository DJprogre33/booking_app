from pydantic import BaseModel


class SHotel(BaseModel):
    name: str
    location: str
    services: list


class SHotelResponse(BaseModel):
    name: str
    location: str
    rooms_quantity: int
    image_id: int
    id: int
    services: list


class SHotelsResponse(BaseModel):
    id: int
    name: str
    location: str
    services: list
    rooms_quantity: int
    image_id: int
    rooms_left: int


