from datetime import date
from typing import Optional

from fastapi import Request
from pydantic import EmailStr

from app.exceptions import IncorrectBookingIdException, RoomCanNotBeBookedException
from app.logger import logger
from app.repositories.bookings import BookingsRepository
from app.schemas.booking import SBookingResponse, SBookingsResponse
from app.services.rooms import RoomsService
from app.tasks.tasks import send_booking_confirmation_email
from app.utils.base import Base


class BookingsService:
    tasks_repo: BookingsRepository = BookingsRepository
    
    @classmethod
    async def get_bookings(cls, user_id: int) -> Optional[list[SBookingsResponse]]:
        return await cls.tasks_repo.get_bookings(user_id=user_id)

    @classmethod
    async def get_booking(cls, booking_id: int, user_id: int) -> SBookingResponse:
        booking = await cls.tasks_repo.find_one_or_none(id=booking_id, user_id=user_id)
        if not booking:
            logger.warning(
                "Incorrect booking id or user_id",
                extra={"user_id": user_id, "booking_id": booking_id},
            )
            raise IncorrectBookingIdException
        return booking
    
    @classmethod
    async def delete_booking(cls, booking_id: int, user_id: int) -> SBookingResponse:
        deleted_booking = await cls.tasks_repo.delete(id=booking_id, user_id=user_id)
        if not deleted_booking:
            logger.warning(
                "Incorrect booking id or user_id",
                extra={"user_id": user_id, "booking_id": booking_id},
            )
            raise IncorrectBookingIdException
        return deleted_booking
    
    @classmethod
    async def add_bookind(
        cls,
        room_id: int,
        date_from: date,
        date_to: date,
        user_id: int,
        user_email: EmailStr
    ) -> SBookingResponse:
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        room = await RoomsService.get_room(room_id=room_id)
        rooms_left = await cls.tasks_repo.get_rooms_left(room_id=room.id)
        if not rooms_left:
            logger.warning("Room can't be booked", extra={"room_id": room_id})
            raise RoomCanNotBeBookedException
        room_price = await cls.tasks_repo.get_room_price(room_id=room_id)
        booking = await cls.tasks_repo.insert_data(
            room_id=room.id,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            price=room_price
        )
        booking_dict = SBookingResponse.model_validate(booking).model_dump()
        # Adds a Celery task to send a reservation notification
        send_booking_confirmation_email.delay(booking_dict, user_email)
        return booking
