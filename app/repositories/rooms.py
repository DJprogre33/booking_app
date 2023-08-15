from datetime import date
from typing import Optional

from sqlalchemy import func, select

from app.models.bookings import Bookings
from app.models.hotels import Hotels
from app.models.rooms import Rooms
from app.schemas.rooms import SRoomResponse
from app.utils.repository import SQLAlchemyRepository


class RoomsRepository(SQLAlchemyRepository):
    model = Rooms

    async def get_available_hotel_rooms(
        self, hotel_id: int, date_from: date, date_to: date
    ) -> Optional[list[SRoomResponse]]:
        get_booked_rooms = (
            select(self.model.id, func.count().label("booked_rooms"))
            .select_from(self.model)
            .join(Bookings, Bookings.room_id == self.model.id)
            .where((Bookings.date_from <= date_to) & (Bookings.date_to >= date_from))
            .group_by(self.model.id)
            .subquery("booked_rooms")
        )
        get_available_rooms = (
            select(
                self.model.id,
                self.model.hotel_id,
                self.model.name,
                self.model.description,
                self.model.services,
                self.model.price,
                self.model.quantity,
                self.model.image_path,
                (self.model.price * (date_to - date_from).days).label("total_cost"),
                (
                    self.model.quantity
                    - func.coalesce(get_booked_rooms.c.booked_rooms, 0)
                ).label("rooms_left"),
            )
            .select_from(self.model)
            .outerjoin(get_booked_rooms, self.model.id == get_booked_rooms.c.id)
            .where(
                (self.model.hotel_id == hotel_id)
                & (
                    (
                        self.model.quantity
                        - func.coalesce(get_booked_rooms.c.booked_rooms, 0)
                    )
                    > 0
                )
            )
        )
        available_rooms = await self.session.execute(get_available_rooms)
        return available_rooms.mappings().all()

    async def get_rooms_left(self, hotel_id: int) -> int:
        """
        The function is used when creating hotels and adding rooms by the owner,
        it checks that the owner does not add more rooms than there are rooms
        in the hotel
        :param hotel_id:
        :return: int
        """
        existing_rooms = (
            select(
                self.model.hotel_id,
                func.sum(self.model.quantity).label("existing_rooms"),
            )
            .select_from(self.model)
            .where(self.model.hotel_id == hotel_id)
            .group_by(self.model.hotel_id)
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
            .outerjoin(existing_rooms, Hotels.id == existing_rooms.c.hotel_id)
            .where(Hotels.id == hotel_id)
        )
        rooms_left = await self.session.execute(rooms_left)
        return rooms_left.scalar()
