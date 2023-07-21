from sqladmin import ModelView

from app.models.bookings import Bookings
from app.models.hotels import Hotels
from app.models.rooms import Rooms
from app.models.users import Users


class UsersAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.email] + [Users.bookings]
    column_details_exclude_list = [Users.hashed_password]
    can_delete = False
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class BookingsAdmin(ModelView, model=Bookings):
    column_list = [c.name for c in Bookings.__table__.columns] + [Bookings.users, Bookings.rooms]
    name = "Booking"
    name_plural = "Bookings"
    icon = "fa-solid fa-book"


class RoomsAdmin(ModelView, model=Rooms):
    column_list = [c.name for c in Rooms.__table__.columns] + [Rooms.hotels, Rooms.bookings]
    name = "Room"
    name_plural = "Rooms"
    icon = "fa-solid fa-bed"


class HotelsAdmin(ModelView, model=Hotels):
    column_list = [c.name for c in Hotels.__table__.columns] + [Hotels.rooms]
    name = "Hotel"
    name_plural = "Hotels"
    icon = "fa-solid fa-hotel"
