from fastapi import APIRouter
from datetime import date
from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotelsResponse, SHotelResponse


router = APIRouter(
    prefix="/hotels",
    tags=["Hotels"]
)


@router.get("/{location}", response_model=list[SHotelsResponse])
async def get_hotels_by_location(
        location: str,
        date_from: date,
        date_to: date
):
    return await HotelDAO.get_hotels_with_available_rooms_by_location(
        location,
        date_from,
        date_to
    )


@router.get("/id/{hotel_id}", response_model=SHotelResponse)
async def get_hotel_by_id(hotel_id: int):
    return await HotelDAO.find_one_or_none(id=hotel_id)