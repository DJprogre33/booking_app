from typing import Type

from app.services.bookings import BookingsService
from app.services.hotels import HotelsService
from app.services.rooms import RoomsService
from app.services.users import UsersService
from app.services.auths import AuthsService


# functions return the service instance
def get_bookings_service() -> Type[BookingsService]:
    return BookingsService


def get_rooms_service() -> Type[RoomsService]:
    return RoomsService


def get_hotels_service() -> Type[HotelsService]:
    return HotelsService


def get_users_service() -> Type[UsersService]:
    return UsersService


def get_auths_service() -> Type[AuthsService]:
    return AuthsService
