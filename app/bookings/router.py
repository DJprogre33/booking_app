from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi_versioning import version

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking, SBookingsResponse
from app.dependencies import get_current_user, validate_data_range
from app.tasks.tasks import send_booking_confirmation_email
from app.users.models import Users

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


@router.get("", response_model=list[SBookingsResponse])
@version(1)
async def get_bookings(request: Request, user: Users = Depends(get_current_user)):
    return await BookingDAO.get_bookings(user_id=user.id)


@router.delete("/{booking_id}")
@version(1)
async def delete_booking(
        booking_id: int,
        request: Request,
        user: Users = Depends(get_current_user)
) -> int:
    return await BookingDAO.delete_booking_by_id(
        user_id=user.id,
        booking_id=booking_id
    )


@router.post("")
@version(1)
async def add_booking(
        room_id: int,
        date_from: date,
        date_to: date,
        validated_dates: tuple = Depends(validate_data_range),
        user: Users = Depends(get_current_user)
):
    date_from, date_to = validated_dates
    booking = await BookingDAO.add_booking(
        user_id=user.id,
        room_id=room_id,
        date_from=date_from,
        date_to=date_to
    )

    booking_dict = SBooking.model_validate(booking).model_dump()
    send_booking_confirmation_email.delay(booking_dict, user.email)
    return booking_dict

