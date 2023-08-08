from datetime import date

from sqlalchemy import delete, func, insert, select

from app.database import async_session_maker
from app.exceptions import IncorrectBookingIdException, RoomCanNotBeBookedException
from app.logger import logger
from app.models.bookings import Bookings
from app.models.rooms import Rooms
from app.utils.repository import SQLAlchemyRepository


class BookingsRepository(SQLAlchemyRepository):
    model = Bookings
    
    @classmethod
    async def add_booking(
        cls, user_id: int, room_id: int, date_from: date, date_to: date
    ):
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
            rooms_left: int = rooms_left.scalar()
            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = (
                    insert(cls.model)
                    .values(
                        room_id=room_id,
                        user_id=user_id,
                        date_from=date_from,
                        date_to=date_to,
                        price=price,
                    )
                    .returning(cls.model)
                )

                new_booking = await session.execute(add_booking)
                await session.commit()

                logger.info("Database query successfully completed")

                return new_booking.scalar()
            logger.warning("Room can't be booked", extra={"room_id": room_id})
            raise RoomCanNotBeBookedException
    
    @classmethod
    async def get_bookings(cls, user_id: int):
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
    
    @classmethod
    async def delete_booking_by_id(cls, user_id: int, booking_id: int) -> int:
        async with async_session_maker() as session:
            logger.info("The database query begins to generate")

            to_delete_entity = (
                delete(cls.model)
                .where((cls.model.user_id == user_id) & (cls.model.id == booking_id))
                .returning(cls.model.id)
            )

            deleted_entity_id = await session.execute(to_delete_entity)

            deleted_entity_id = deleted_entity_id.scalars().one_or_none()

            if deleted_entity_id is None:
                logger.warning(
                    "Incorrect booking id or user_id",
                    extra={"user_id": user_id, "booking_id": booking_id},
                )
                err = IncorrectBookingIdException
                err.detail = "Incorrect booking id or user_id"
                raise err

            await session.commit()

            logger.info("Database query successfully completed")

            return deleted_entity_id
