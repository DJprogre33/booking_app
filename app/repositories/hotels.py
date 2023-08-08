from datetime import date
from typing import Optional

from sqlalchemy import func, select

from app.database import async_session_maker
from app.logger import logger
from app.models.bookings import Bookings
from app.models.hotels import Hotels
from app.models.rooms import Rooms
from app.utils.repository import SQLAlchemyRepository
from app.schemas.hotels import SHotelsResponse


class HotelsRepository(SQLAlchemyRepository):
    model = Hotels
    
    @classmethod
    async def get_hotels_by_location_and_time(
        cls, location: str, date_from: date, date_to: date
    ) -> Optional[list[SHotelsResponse]]:
        async with async_session_maker() as session:
            logger.info("The database query begins to generate")

            get_booked_rooms = (
                select(Rooms.hotel_id, func.count().label("booked_rooms"))
                .select_from(Bookings)
                .join(Rooms, Bookings.room_id == Rooms.id)
                .where(
                    (Bookings.date_from <= date_to) & (Bookings.date_to >= date_from)
                )
                .group_by(Rooms.hotel_id)
                .subquery("booked_rooms")
            )

            get_available_hotels = (
                select(
                    cls.model.id,
                    cls.model.name,
                    cls.model.location,
                    cls.model.services,
                    cls.model.rooms_quantity,
                    cls.model.image_path,
                    (
                        cls.model.rooms_quantity
                        - func.coalesce(get_booked_rooms.c.booked_rooms, 0)
                    ).label("rooms_left"),
                )
                .select_from(cls.model)
                .outerjoin(
                    get_booked_rooms, cls.model.id == get_booked_rooms.c.hotel_id
                )
                .where(
                    (cls.model.location.ilike(f"%{location}%"))
                    & (
                        (
                            cls.model.rooms_quantity
                            - func.coalesce(get_booked_rooms.c.booked_rooms, 0)
                        )
                        > 0
                    )
                )
            )
            available_hotels = await session.execute(get_available_hotels)
            logger.info("Database query successfully completed")
            return available_hotels.mappings().all()
