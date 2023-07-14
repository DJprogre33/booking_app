from app.dao.base import BaseDAO
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.bookings.models import Bookings
from datetime import date
from app.database import async_session_maker
from sqlalchemy import select, func


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def get_hotels_with_available_rooms_by_location(
            cls,
            location: str,
            date_from: date,
            date_to: date
    ) -> list[dict]:

        async with async_session_maker() as session:

            get_booked_rooms = select(
                Rooms.hotel_id,
                func.count().label("booked_rooms")
            ).select_from(Bookings).join(
                Rooms,
                Bookings.room_id == Rooms.id
            ).where(
                (Bookings.date_from <= date_to) &
                (Bookings.date_to >= date_from)
            ).group_by(Rooms.hotel_id).subquery("booked_rooms")

            get_available_hotels = select(
                Hotels.id,
                Hotels.name,
                Hotels.location,
                Hotels.services,
                Hotels.rooms_quantity,
                Hotels.image_id,
                (Hotels.rooms_quantity - func.coalesce(get_booked_rooms.c.booked_rooms, 0)).label("rooms_left")
            ).select_from(Hotels).outerjoin(
                get_booked_rooms,
                Hotels.id == get_booked_rooms.c.hotel_id
            ).where(Hotels.location.ilike(f"%{location}%"))

            # print(query.compile(engine, compile_kwargs={"literal_binds": True}))

            available_hotels = await session.execute(get_available_hotels)
            return available_hotels.mappings().all()

