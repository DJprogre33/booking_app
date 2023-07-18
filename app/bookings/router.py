from fastapi import APIRouter, Request, Depends
from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBookingsResponse, SBooking
from app.users.models import Users
from app.users.dependencies import get_current_user
from datetime import date
from app.tasks.tasks import send_booking_confirmation_email


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


# @router.get("", response_model=list[SBookingsResponse])
@router.get("")
async def get_bookings(request: Request, user: Users = Depends(get_current_user)):
    return await BookingDAO.get_bookings(user_id=user.id)


@router.delete("/{booking_id}")
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
async def add_booking(
        room_id: int,
        date_from: date,
        date_to: date,
        user: Users = Depends(get_current_user)
):
    booking = await BookingDAO.add_booking(
        user_id=user.id,
        room_id=room_id,
        date_from=date_from,
        date_to=date_to
    )

    booking_dict = SBooking.model_validate(booking).model_dump()
    send_booking_confirmation_email.delay(booking_dict, user.email)
    return booking_dict

