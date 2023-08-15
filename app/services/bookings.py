from datetime import date
from typing import Optional

from pydantic import EmailStr

from app.exceptions import IncorrectBookingIdException, RoomCanNotBeBookedException
from app.logger import logger
from app.schemas.booking import SBookingResponse, SBookingsResponse
from app.services.rooms import RoomsService
from app.tasks.tasks import send_booking_confirmation_email
from app.utils.base import Base
from app.utils.transaction_manager import ITransactionManager


class BookingsService:
    @staticmethod
    async def get_bookings(
        transaction_manager: ITransactionManager, user_id: int
    ) -> Optional[list[SBookingsResponse]]:
        async with transaction_manager:
            bookings = await transaction_manager.bookings.get_bookings(user_id=user_id)
            await transaction_manager.commit()
            return bookings

    @staticmethod
    async def get_booking(
        transaction_manager: ITransactionManager, booking_id: int, user_id: int
    ) -> SBookingResponse:
        async with transaction_manager:
            booking = await transaction_manager.bookings.find_one_or_none(
                id=booking_id, user_id=user_id
            )
            if not booking:
                logger.warning(
                    "Incorrect booking id or user_id",
                    extra={"user_id": user_id, "booking_id": booking_id},
                )
                raise IncorrectBookingIdException
            await transaction_manager.commit()
            return booking

    @staticmethod
    async def delete_booking(
        transaction_manager: ITransactionManager, booking_id: int, user_id: int
    ) -> SBookingResponse:
        async with transaction_manager:
            deleted_booking = await transaction_manager.bookings.delete(
                id=booking_id, user_id=user_id
            )
            if not deleted_booking:
                logger.warning(
                    "Incorrect booking id or user_id",
                    extra={"user_id": user_id, "booking_id": booking_id},
                )
                raise IncorrectBookingIdException
            await transaction_manager.commit()
            return deleted_booking

    @staticmethod
    async def add_bookind(
        transaction_manager: ITransactionManager,
        room_id: int,
        date_from: date,
        date_to: date,
        user_id: int,
        user_email: EmailStr,
    ) -> SBookingResponse:
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        async with transaction_manager:
            room = await RoomsService().get_room(
                transaction_manager=transaction_manager, room_id=room_id
            )
            rooms_left = await transaction_manager.bookings.get_rooms_left(
                room_id=room_id, date_from=date_from, date_to=date_to
            )
            if not rooms_left:
                logger.warning("Room can't be booked", extra={"room_id": room_id})
                raise RoomCanNotBeBookedException
            room_price = await transaction_manager.bookings.get_room_price(
                room_id=room_id
            )
            new_booking = await transaction_manager.bookings.insert_data(
                room_id=room.id,
                user_id=user_id,
                date_from=date_from,
                date_to=date_to,
                price=room_price,
            )
            booking_dict = SBookingResponse.model_validate(new_booking).model_dump()
            # Adds a Celery task to send a reservation notification
            send_booking_confirmation_email.delay(booking_dict, user_email)
            await transaction_manager.commit()
            return new_booking
