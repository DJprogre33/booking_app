from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_versioning import version

from app.dependencies import TManagerDep, get_current_user
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
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_user)
):
    """Returns all orders of the current authenticated user"""
    bookings = await BookingsService().get_bookings(
        transaction_manager=transaction_manager,
        user_id=current_user.id
    )
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
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_user)
):
    """Returns specific booking of the current authenticated user by id"""
    async with transaction_manager:
        booking = await BookingsService().get_booking(
            transaction_manager=transaction_manager,
            booking_id=booking_id,
            user_id=current_user.id
        )
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
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_user)
):
    """Deletes specific booking of the current authenticated user by id"""
    deleted_booking = await BookingsService().delete_booking(
        transaction_manager=transaction_manager,
        booking_id=booking_id,
        user_id=current_user.id
    )
    logger.info(
        "The booking by id was successfully deleted",
        extra={"booking_id": deleted_booking.id},
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
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_user)
):
    """Adds bookings for the current user"""
    new_booking = await BookingsService().add_bookind(
        transaction_manager=transaction_manager,
        room_id=room_id,
        date_from=date_from,
        date_to=date_to,
        user_id=current_user.id,
        user_email=current_user.email
    )
    logger.info(
        "Booking has been successfully created", extra={"booking_id": new_booking.id}
    )
    return new_booking
