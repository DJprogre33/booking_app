from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from fastapi_versioning import version

from app.dependencies import get_bookings_service, get_current_user
from app.exceptions import SExstraResponse
from app.logger import logger
from app.models.users import Users
from app.schemas.booking import SBookingResponse, SBookingsResponse
from app.services.bookings import BookingsService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get(
    "",
    response_model=Optional[list[SBookingsResponse]],
    responses={
        401: {"model": SExstraResponse}
    }
)
@version(1)
async def get_bookings(
    tasks_service: Annotated[BookingsService, Depends(get_bookings_service)],
    current_user: Users = Depends(get_current_user)
):
    """Returns all orders of the current authenticated user"""
    bookings = await tasks_service.get_bookings(user_id=current_user.id)
    logger.info(
        "The list of bookings was successfully received",
        extra={"bookings_nums": len(bookings)},
    )
    return bookings

@router.get(
    "/{booking_id}",
    response_model=SBookingResponse,
    responses={
        401: {"model": SExstraResponse},
        404: {"model": SExstraResponse}
    }
)
@version(1)
async def get_booking(
    booking_id: int,
    tasks_service: Annotated[BookingsService, Depends(get_bookings_service)],
    current_user: Users = Depends(get_current_user)
):
    """Returns specific booking of the current authenticated user by id"""
    booking = await tasks_service.get_booking(booking_id=booking_id, user_id=current_user.id)
    logger.info(
        "The booking by id was successfully received",
        extra={"booking_id": booking.id},
    )
    return booking


@router.delete(
    "/{booking_id}",
    responses={
        401: {"model": SExstraResponse},
        404: {"model": SExstraResponse}
    }
)
@version(1)
async def delete_booking(
    booking_id: int,
    tasks_service: Annotated[BookingsService, Depends(get_bookings_service)],
    current_user: Users = Depends(get_current_user)
):
    """Deletes specific booking of the current authenticated user by id"""
    deleted_booking = await tasks_service.delete_booking(booking_id=booking_id, user_id=current_user.id)
    logger.info(
        "The booking by id was successfully deleted",
        extra={"booking_id": booking_id},
    )
    return deleted_booking


@router.post(
    "/{room_id}",
    response_model=SBookingResponse,
    responses={
        400: {"model": SExstraResponse},
        401: {"model": SExstraResponse},
        404: {"model": SExstraResponse}
    }
)
@version(1)
async def add_booking(
    room_id: int,
    date_from: date,
    date_to: date,
    tasks_service: Annotated[BookingsService, Depends(get_bookings_service)],
    current_user: Users = Depends(get_current_user)
):
    """Adds bookings for the current user"""
    booking = await tasks_service.add_bookind(
        room_id=room_id,
        date_from=date_from,
        date_to=date_to,
        user_id=current_user.id,
        user_email=current_user.email
    )
    logger.info(
        "Booking has been successfully created", extra={"booking_id": booking.id}
    )
    return booking
