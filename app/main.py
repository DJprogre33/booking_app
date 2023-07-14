from fastapi import FastAPI, Query, Depends
from typing import Optional
from datetime import date
from pydantic import BaseModel

from app.bookings.router import router as router_bookings
from app.users.router import router as router_users
from app.hotels.router import router as router_hotels
from app.hotels.rooms.router import router as router_rooms


app = FastAPI()

app.include_router(router_rooms)
app.include_router(router_hotels)
app.include_router(router_users)
app.include_router(router_bookings)


class HotelSearchArgs:
    def __init__(
            self,
            location: str,
            date_from: date,
            date_to: date,
            has_spa: Optional[bool] = None,
            stars: Optional[int] = Query(None, ge=1, le=5)
    ):
        self.location = location
        self.date_from = date_from
        self.date_to = date_to
        self.has_spa = has_spa
        self.stars = stars


class SHotel(BaseModel):
    adress: str
    name: str
    stars: int


@app.get("/hotels")
def get_hotels(
        search_args: HotelSearchArgs = Depends()
):
    hotels = [
        {
            "adress": "Ул. Гагарина 34",
            "name": "Super Hotel",
            "stars": 5
        }
    ]
    return hotels



