from fastapi import APIRouter
from datetime import date
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.schemas import SRoomsResponse


router = APIRouter(
    prefix="/hotels",
    tags=["Hotels", "Rooms"]
)


@router.get("/{hotel_id}/rooms", response_model=list[SRoomsResponse])
async def get_available_hotel_rooms(
        hotel_id: int,
        date_from: date,
        date_to: date
):
    return await RoomDAO.get_available_hotel_rooms(
        hotel_id=hotel_id,
        date_from=date_from,
        date_to=date_to
    )