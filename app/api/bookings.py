from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi_versioning import version

from app.api.dependencies import get_bookings_service
from app.schemas.booking import SBookingsResponse
from app.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("", response_model=list[SBookingsResponse])
@version(1)
async def get_bookings(
    request: Request,
    tasks_service: Annotated[BookingService, Depends(get_bookings_service)],
):
    return await tasks_service.get_bookings(request)


@router.delete("/{booking_id}")
@version(1)
async def delete_booking(
    booking_id: int,
    request: Request,
    tasks_service: Annotated[BookingService, Depends(get_bookings_service)],
) -> int:
    return await tasks_service.delete_booking_by_id(booking_id, request)


@router.post("")
@version(1)
async def add_booking(
    room_id: int,
    date_from: date,
    date_to: date,
    request: Request,
    tasks_service: Annotated[BookingService, Depends(get_bookings_service)],
):
    return await tasks_service.add_bookind(
        room_id=room_id,
        date_from=date_from,
        date_to=date_to,
        request=request
    )
