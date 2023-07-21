from app.repositories.bookings import BookingsRepository
from app.repositories.hotels import HotelsRepository
from app.repositories.rooms import RoomsRepository
from app.repositories.users import UsersRepository
from app.services.bookings import BookingService
from app.services.hotels import HotelsService
from app.services.rooms import RoomsService
from app.services.users import UsersService


def get_bookings_service():
    return BookingService(BookingsRepository)

def get_rooms_service():
    return RoomsService(RoomsRepository)

def get_hotels_service():
    return HotelsService(HotelsRepository)

def get_users_service():
    return UsersService(UsersRepository)
