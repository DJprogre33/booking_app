from datetime import date, datetime, timedelta

from app.exceptions import IncorrectDataRangeException, AccessDeniedException, IncorrectHotelIDException
from app.logger import logger
from app.repositories.hotels import HotelsRepository

from app.models.hotels import Hotels

class Base:
    """
    Contains general useful functions for the project
    """

    @staticmethod
    def validate_data_range(date_from: date, date_to: date) -> tuple:
        booking_period = date_to - date_from

        if date_from < datetime.utcnow().date():
            logger.error(
                "date_from can't be earlier then now",
                extra={"date_from": date_from, "date_to": date_to},
            )
            raise IncorrectDataRangeException()

        if booking_period < timedelta(days=1) or booking_period > timedelta(days=90):
            logger.error(
                "Incorrect data range",
                extra={"date_from": date_from, "date_to": date_to},
            )
            raise IncorrectDataRangeException()

        return date_from, date_to

    @staticmethod
    async def check_owner(task_repo: HotelsRepository, hotel_id: int, user_id: int) -> Hotels:

        hotel = await task_repo.find_one_or_none(id=hotel_id)

        if not hotel:
            logger.warning("Incorrect hotel id", extra={"hotel_id": hotel_id})
            raise IncorrectHotelIDException()

        if hotel.owner_id != user_id:
            logger.warning("User isn't an owner", extra={"hotel_id": hotel_id, "user_id": user_id})
            raise AccessDeniedException()

        return hotel
