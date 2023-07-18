from datetime import date

from sqlalchemy import func, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class RoomDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def get_available_hotel_rooms(
            cls,
            hotel_id: int,
            date_from: date,
            date_to: date
    ) -> list[dict]:

        async with async_session_maker() as session:

            get_booked_rooms = select(
                Rooms.id,
                func.count().label("booked_rooms")
            ).select_from(Bookings).join(
                Rooms,
                Bookings.room_id == Rooms.id
            ).where(
                (Bookings.date_from <= date_to) &
                (Bookings.date_to >= date_from)
            ).group_by(Rooms.id).subquery("booked_rooms")

            get_available_rooms = select(
                Rooms.id,
                Rooms.hotel_id,
                Rooms.name,
                Rooms.description,
                Rooms.services,
                Rooms.price,
                Rooms.quantity,
                Rooms.image_id,
                (Rooms.price * (date_to - date_from).days).label("total_cost"),
                (Rooms.quantity - func.coalesce(get_booked_rooms.c.booked_rooms, 0)).label("rooms_left")
            ).select_from(Rooms).outerjoin(
                get_booked_rooms,
                Rooms.id == get_booked_rooms.c.id
            ).where(Rooms.hotel_id == hotel_id)

            available_rooms = await session.execute(get_available_rooms)

            return available_rooms.mappings().all()

