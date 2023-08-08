from datetime import date

from sqlalchemy import func, select

from app.database import async_session_maker
from app.models.bookings import Bookings
from app.models.hotels import Hotels
from app.models.rooms import Rooms
from app.utils.repository import SQLAlchemyRepository
from app.schemas.hotels import SHotelsResponse
from typing import Optional


class RoomsRepository(SQLAlchemyRepository):
    model = Rooms

    @classmethod
    async def get_available_hotel_rooms(
        cls, hotel_id: int, date_from: date, date_to: date
    ) -> Optional[list[SHotelsResponse]]:
        async with async_session_maker() as session:
            get_booked_rooms = (
                select(cls.model.id, func.count().label("booked_rooms"))
                .select_from(cls.model)
                .join(Bookings, Bookings.room_id == cls.model.id)
                .where(
                    (Bookings.date_from <= date_to) & (Bookings.date_to >= date_from)
                )
                .group_by(cls.model.id)
                .subquery("booked_rooms")
            )
            get_available_rooms = (
                select(
                    cls.model.id,
                    cls.model.hotel_id,
                    cls.model.name,
                    cls.model.description,
                    cls.model.services,
                    cls.model.price,
                    cls.model.quantity,
                    cls.model.image_path,
                    (cls.model.price * (date_to - date_from).days).label("total_cost"),
                    (
                        cls.model.quantity
                        - func.coalesce(get_booked_rooms.c.booked_rooms, 0)
                    ).label("rooms_left"),
                )
                .select_from(cls.model)
                .outerjoin(get_booked_rooms, cls.model.id == get_booked_rooms.c.id)
                .where(
                    (cls.model.hotel_id == hotel_id)
                    & (
                        (
                            cls.model.quantity
                            - func.coalesce(get_booked_rooms.c.booked_rooms, 0)
                        )
                        > 0
                    )
                )
            )
            available_rooms = await session.execute(get_available_rooms)
            return available_rooms.mappings().all()
    
    @classmethod
    async def get_rooms_left(cls, hotel_id: int) -> int:
        """
        The function is used when creating hotels and adding rooms by the owner,
        it checks that the owner does not add more rooms than there are rooms
        in the hotel
        :param hotel_id:
        :return:
        """
        async with async_session_maker() as session:
            existing_rooms = (
                select(
                    cls.model.hotel_id,
                    func.sum(cls.model.quantity).label("existing_rooms"),
                )
                .select_from(cls.model)
                .where(cls.model.hotel_id == hotel_id)
                .group_by(cls.model.hotel_id)
                .subquery("existing_rooms")
            )
            rooms_left = (
                select(
                    (
                        Hotels.rooms_quantity
                        - func.coalesce(existing_rooms.c.existing_rooms, 0)
                    ).label("rooms_left")
                )
                .select_from(Hotels)
                .join(existing_rooms, Hotels.id == existing_rooms.c.hotel_id)
            )
            rooms_left = await session.execute(rooms_left)
            return rooms_left.scalar()
