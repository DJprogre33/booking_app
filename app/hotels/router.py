from asyncio import sleep
from datetime import date

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from fastapi_versioning import version

from app.dependencies import validate_data_range
from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotelResponse, SHotelsResponse

router = APIRouter(
    prefix="/hotels",
    tags=["Hotels"]
)


@router.get("/{location}", response_model=list[SHotelsResponse])
@cache(expire=60)
@version(1)
async def get_hotels_by_location_and_time(
        location: str,
        date_from: date,
        date_to: date,
        validated_dates: tuple = Depends(validate_data_range)
):
    date_from, date_to = validated_dates
    await sleep(3)
    return await HotelDAO.get_hotels_with_available_rooms_by_location(
        location,
        date_from,
        date_to
    )


@router.get("/id/{hotel_id}", response_model=SHotelResponse)
@version(1)
async def get_hotel_by_id(hotel_id: int):
    return await HotelDAO.find_one_or_none(id=hotel_id)