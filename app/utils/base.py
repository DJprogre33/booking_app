from datetime import date, datetime, timedelta

from app.exceptions import IncorrectDataRangeException
from app.logger import logger


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
            raise IncorrectDataRangeException

        if booking_period < timedelta(days=1) or booking_period > timedelta(days=90):
            logger.error(
                "Incorrect data range",
                extra={"date_from": date_from, "date_to": date_to},
            )
            raise IncorrectDataRangeException
        return date_from, date_to
