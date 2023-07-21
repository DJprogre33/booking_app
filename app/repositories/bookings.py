from datetime import date

from sqlalchemy import delete, func, insert, select

from app.database import async_session_maker
from app.exceptions import IncorrectBookingIdException, RoomCanNotBeBookedException
from app.models.bookings import Bookings
from app.models.rooms import Rooms
from app.utils.repository import SQLAlchemyRepository


class BookingsRepository(SQLAlchemyRepository):
    model = Bookings

    async def add_booking(
        self, user_id: int, room_id: int, date_from: date, date_to: date
    ):
        async with async_session_maker() as session:
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

            rooms_left = await session.execute(get_rooms_left)
            rooms_left: int = rooms_left.scalar()
            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = (
                    insert(self.model)
                    .values(
                        room_id=room_id,
                        user_id=user_id,
                        date_from=date_from,
                        date_to=date_to,
                        price=price,
                    )
                    .returning(self.model)
                )

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.scalar()
            raise RoomCanNotBeBookedException()

    async def get_bookings(self, user_id: int):
        async with async_session_maker() as session:
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
                    Rooms.image_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                )
                .select_from(self.model)
                .join(Rooms, self.model.room_id == Rooms.id)
                .where(self.model.user_id == user_id)
            )

            result = await session.execute(get_bookings)

            return result.mappings().all()

    async def delete_booking_by_id(self, user_id: int, booking_id: int) -> int:
        async with async_session_maker() as session:
            to_delete_entity = (
                delete(self.model)
                .where((self.model.user_id == user_id) & (self.model.id == booking_id))
                .returning(self.model.id)
            )

            deleted_entity_id = await session.execute(to_delete_entity)

            deleted_entity_id = deleted_entity_id.scalars().one_or_none()

            if deleted_entity_id is None:
                raise IncorrectBookingIdException()

            await session.commit()

            return deleted_entity_id
