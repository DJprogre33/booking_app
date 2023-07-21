from pydantic import BaseModel


class SHotel(BaseModel):
    name: str
    location: str
    services: list
    rooms_quantity: int


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

