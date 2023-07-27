from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SBookingsResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int
    image_path: Optional[str]
    name: str
    description: Optional[str]
    services: list


class SBookingResponce(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int
