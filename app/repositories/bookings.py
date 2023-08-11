from datetime import date
from typing import Optional

from sqlalchemy import func, select

from app.logger import logger
from app.models.bookings import Bookings
from app.models.rooms import Rooms
from app.schemas.booking import SBookingsResponse
from app.utils.repository import SQLAlchemyRepository


class BookingsRepository(SQLAlchemyRepository):
    model = Bookings

    async def get_rooms_left(
        self, room_id: int, date_from: date, date_to: date
    ) -> int:
        logger.info("The database query begins to generate")
        booked_rooms = (
            select(self.model)
            .where(
                (self.model.room_id == room_id)
                & (self.model.date_from <= date_to)
                & (self.model.date_to >= date_from)
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
        rooms_left = await self.session.execute(get_rooms_left)
        logger.info("Database query successfully completed")
        return rooms_left.scalar()

    async def get_room_price(self, room_id: int) -> int:
        logger.info("The database query begins to generate")
        room_price = select(Rooms.price).filter_by(id=room_id)
        price = await self.session.execute(room_price)
        logger.info("Database query successfully completed")
        return price.scalar()

    async def get_bookings(self, user_id: int) -> Optional[list[SBookingsResponse]]:
        logger.info("The database query begins to generate")
        get_bookings = (
            select(
                self.model.id,
                self.model.room_id,
                self.model.user_id,
                self.model.date_from,
                self.model.date_to,
                self.model.price,
                self.model.total_cost,
                self.model.total_days,
                Rooms.image_path,
                Rooms.name,
                Rooms.description,
                Rooms.services,
            )
            .select_from(self.model)
            .join(Rooms, self.model.room_id == Rooms.id)
            .where(self.model.user_id == user_id)
        )
        result = await self.session.execute(get_bookings)
        logger.info("Database query successfully completed")
        return result.mappings().all()
