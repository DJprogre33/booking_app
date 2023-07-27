from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi_versioning import version

from app.api.dependencies import get_bookings_service
from app.logger import logger
from app.schemas.booking import SBookingResponce, SBookingsResponse
from app.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("", response_model=list[SBookingsResponse])
@version(1)
async def get_bookings(
    request: Request,
    tasks_service: Annotated[BookingService, Depends(get_bookings_service)],
):
    """Returns all orders of the current authenticated user"""
    bookings = await tasks_service.get_bookings(request)

    logger.info(
        "The list of bookings was successfully received",
        extra={"bookings_nums": len(bookings)},
    )

    return bookings


@router.delete("/{booking_id}")
@version(1)
async def delete_booking(
    booking_id: int,
    request: Request,
    tasks_service: Annotated[BookingService, Depends(get_bookings_service)],
) -> dict:
    deleted_booking_id = await tasks_service.delete_booking_by_id(booking_id, request)

    logger.info(
        "The booking was successfully removed ",
        extra={"deleted_booking_id": deleted_booking_id},
    )

    return {"deleted_booking_id": deleted_booking_id}


@router.post("", response_model=SBookingResponce)
@version(1)
async def add_booking(
    room_id: int,
    date_from: date,
    date_to: date,
    request: Request,
    tasks_service: Annotated[BookingService, Depends(get_bookings_service)],
):
    booking = await tasks_service.add_bookind(
        room_id=room_id, date_from=date_from, date_to=date_to, request=request
    )

    logger.info(
        "Booking has been successfully created", extra={"booking_id": booking["id"]}
    )

    return booking
