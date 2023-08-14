from fastapi import HTTPException, status
from pydantic import BaseModel


class SExstraResponse(BaseModel):
    """Class for extra responses in OpenAPI doc"""
    detail: str


class BookingAppException(HTTPException):
    """Base class for all project exceptions"""
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistException(BookingAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "The user alredy exists"


class IncorrectCredentials(BookingAppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Incorrect credentials, email should be valid (user@example.com)"


class IncorrectEmailOrPasswordException(BookingAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid email or password"


class TokenExpiredException(BookingAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "The token has expired"


class TokenAbsentException(BookingAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "The token is missing"


class IncorrectTokenFormatException(BookingAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect token format"


class InvalidTokenUserIDException(BookingAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token user id"


class RoomCanNotBeBookedException(BookingAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "There are no rooms available"


class IncorrectDataRangeException(BookingAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = (
        "Incorrect data range, data range must be"
        "1 <= data_to - data_from <= 90"
        "and date_from can't be earlier then now"
    )


class IncorrectBookingIdException(BookingAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Booking with this id was not found"


class AccessDeniedException(BookingAppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "You do not have permissions to use this endpoint"


class IncorrectHotelIDException(BookingAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "The hotel not found by id"


class RoomLimitExceedException(BookingAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "The number of rooms exceeds the total number of rooms in the hotel"


class IncorrectIDException(BookingAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "The entity not found by id"


class IncorrectRoomIDException(BookingAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "The room not found by id"
