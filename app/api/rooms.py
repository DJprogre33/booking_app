from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_versioning import version

from app.api.dependencies import get_rooms_service
from app.schemas.rooms import SRoomsResponse
from app.services.rooms import RoomsService


router = APIRouter(prefix="/hotels", tags=["Hotels", "Rooms"])


@router.get("/{hotel_id}/rooms", response_model=list[SRoomsResponse])
@version(1)
async def get_available_hotel_rooms(
    hotel_id: int,
    date_from: date,
    date_to: date,
    tasks_service: Annotated[RoomsService, Depends(get_rooms_service)],
):
    return await tasks_service.get_availible_hotel_rooms(
        hotel_id=hotel_id, date_from=date_from, date_to=date_to
    )


@router.post("/{hotel_id}/{room_id}")
@version(1)
async def create_room():
    pass


@router.delete("/{hotel_id}/{room_id}")
@version(1)
async def delete_room():
    pass