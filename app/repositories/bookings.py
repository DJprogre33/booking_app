from datetime import date
from typing import Optional

from sqlalchemy import func, select

from app.database import async_session_maker
from app.logger import logger
from app.models.bookings import Bookings
from app.models.rooms import Rooms
from app.schemas.booking import SBookingsResponse
from app.utils.repository import SQLAlchemyRepository


class BookingsRepository(SQLAlchemyRepository):
    model = Bookings

    @classmethod
    async def get_rooms_left(
        cls, room_id: int, date_from: date, date_to: date
    ) -> int:
        async with async_session_maker() as session:
            logger.info("The database query begins to generate")
            booked_rooms = (
                select(cls.model)
                .where(
                    (cls.model.room_id == room_id)
                    & (cls.model.date_from <= date_to)
                    & (cls.model.date_to >= date_from)
                )
                .cte("booked_rooms")
            )
            get_rooms_left = (
                select((Rooms.quantity - func.count(booked_rooms.c.room_id)))
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .where(Rooms.id == room_id)
                .group_by(Rooms.quantity, booked_rooms.c.room_id)
            )
            rooms_left = await session.execute(get_rooms_left)
            logger.info("Database query successfully completed")
            return rooms_left.scalar()

    @classmethod
    async def get_room_price(cls, room_id: int) -> int:
        async with async_session_maker() as session:
            logger.info("The database query begins to generate")
            room_price = select(Rooms.price).filter_by(id=room_id)
            price = await session.execute(room_price)
            logger.info("Database query successfully completed")
            return price.scalar()

    @classmethod
    async def get_bookings(cls, user_id: int) -> Optional[list[SBookingsResponse]]:
        async with async_session_maker() as session:
            logger.info("The database query begins to generate")
            get_bookings = (
                select(
                    cls.model.id,
                    cls.model.room_id,
                    cls.model.user_id,
                    cls.model.date_from,
                    cls.model.date_to,
                    cls.model.price,
                    cls.model.total_cost,
                    cls.model.total_days,
                    Rooms.image_path,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                )
                .select_from(cls.model)
                .join(Rooms, cls.model.room_id == Rooms.id)
                .where(cls.model.user_id == user_id)
            )
            result = await session.execute(get_bookings)
            logger.info("Database query successfully completed")
            return result.mappings().all()
