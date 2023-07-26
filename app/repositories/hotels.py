from datetime import date

from sqlalchemy import func, select

from app.database import async_session_maker
from app.models.bookings import Bookings
from app.models.hotels import Hotels
from app.models.rooms import Rooms
from app.utils.repository import SQLAlchemyRepository
from app.logger import logger

class HotelsRepository(SQLAlchemyRepository):
    model = Hotels

    async def get_hotels_by_location_and_time(
            self,
            location: str,
            date_from: date,
            date_to: date
    ) -> list[dict]:

        async with async_session_maker() as session:
            logger.info("The database query begins to generate")

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
                self.model.id,
                self.model.name,
                self.model.location,
                self.model.services,
                self.model.rooms_quantity,
                self.model.image_path,
                (self.model.rooms_quantity - func.coalesce(get_booked_rooms.c.booked_rooms, 0)).label("rooms_left")
            ).select_from(self.model).outerjoin(
                get_booked_rooms,
                self.model.id == get_booked_rooms.c.hotel_id
            ).where(
                (self.model.location.ilike(f"%{location}%")) &
                ((self.model.rooms_quantity - func.coalesce(get_booked_rooms.c.booked_rooms, 0)) > 0)
            )

            available_hotels = await session.execute(get_available_hotels)

            logger.info("Database query successfully completed")
            return available_hotels.mappings().all()
