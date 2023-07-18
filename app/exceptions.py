from fastapi import HTTPException, status


class BookingAppException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )


class UserAlreadyExistException(BookingAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "The user alredy exists"


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


class InvalidTokenUserIException(BookingAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token user id"


class RoomCanNotBeBookedException(BookingAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "There are no rooms available"


class IncorrectDataRangeException(BookingAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Incorrect data range, data range must be 1 <= data_to - data_from <= 90"


class IncorrectBookingIdException(BookingAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Booking with this id was not found"