from datetime import date

from fastapi import Request

from app.auth.auth import get_current_user, get_token
from app.repositories.bookings import BookingsRepository
from app.schemas.booking import SBookingResponse
from app.tasks.tasks import send_booking_confirmation_email
from app.utils.base import Base


class BookingsService:
    tasks_repo: BookingsRepository = BookingsRepository
    
    @classmethod
    async def get_bookings(cls, request: Request):
        token = get_token(request)
        user = await get_current_user(token)
        return await cls.tasks_repo.get_bookings(user_id=user.id)
    
    @classmethod
    async def delete_booking_by_id(cls, booking_id: int, request: Request):
        token = get_token(request)
        user = await get_current_user(token)
        return await cls.tasks_repo.delete_booking_by_id(
            user_id=user.id, booking_id=booking_id
        )
    
    @classmethod
    async def add_bookind(
        cls,
        room_id: int,
        date_from: date,
        date_to: date,
        request: Request,
    ):
        token = get_token(request)
        user = await get_current_user(token)
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        booking = await cls.tasks_repo.add_booking(
            user_id=user.id, room_id=room_id, date_from=date_from, date_to=date_to
        )
        booking_dict = SBookingResponse.model_validate(booking).model_dump()
        send_booking_confirmation_email.delay(booking_dict, user.email)
        return booking_dict
