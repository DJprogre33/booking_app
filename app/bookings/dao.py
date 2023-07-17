from app.database import async_session_maker
from sqlalchemy import select, func, insert, delete
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from datetime import date
from app.hotels.rooms.models import Rooms
from app.database import engine, async_session_maker


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add_booking(
            cls,
            user_id: int,
            room_id: int,
            date_from: date,
            date_to: date
    ):
        async with async_session_maker() as session:
            booked_rooms = select(cls.model).where(
                (cls.model.room_id == room_id) &
                (cls.model.date_from <= date_to) &
                (cls.model.date_to >= date_from)
            ).cte("booked_rooms")

            get_rooms_left = (
                select(
                    (Rooms.quantity - func.count(booked_rooms.c.room_id))
                )
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .where(Rooms.id == room_id)
                .group_by(Rooms.quantity, booked_rooms.c.room_id)
            )

            # print(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))

            rooms_left = await session.execute(get_rooms_left)
            rooms_left: int = rooms_left.scalar()
            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = insert(Bookings).values(
                    room_id=room_id,
                    user_id=user_id,
                    date_from=date_from,
                    date_to=date_to,
                    price=price
                ).returning(Bookings)

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.scalar()
            else:
                return None

    @classmethod
    async def get_bookings(
            cls,
            user_id: int
    ):
        async with async_session_maker() as session:
            get_bookings = select(
                Bookings.room_id,
                Bookings.user_id,
                Bookings.date_from,
                Bookings.date_to,
                Bookings.price,
                Bookings.total_cost,
                Bookings.total_days,
                Rooms.image_id,
                Rooms.name,
                Rooms.description,
                Rooms.services
            ).select_from(Bookings).join(
                Rooms,
                Bookings.room_id == Rooms.id
            ).where(
                Bookings.user_id == user_id
            )

            result = await session.execute(get_bookings)

            return result.mappings().all()

    @classmethod
    async def delete_booking_by_id(
            cls,
            user_id: int,
            booking_id: int
    ) -> int:
        async with async_session_maker() as session:
            to_delete_entity = delete(cls.model).where(
                (cls.model.user_id == user_id) &
                (cls.model.id == booking_id)
            ).returning(cls.model.id)

            deleted_entity_id = await session.execute(to_delete_entity)

            deleted_entity_id = deleted_entity_id.scalars().one_or_none()

            if None:
                # отрефакторить на кастомное
                raise Exception

            await session.commit()

            return deleted_entity_id
