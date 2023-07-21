from datetime import date

from sqlalchemy import func, select

from app.database import async_session_maker
from app.models.bookings import Bookings
from app.models.rooms import Rooms
from app.utils.repository import SQLAlchemyRepository


class RoomsRepository(SQLAlchemyRepository):
    model = Rooms

    async def get_available_hotel_rooms(
            self,
            hotel_id: int,
            date_from: date,
            date_to: date
    ) -> list[dict]:

        async with async_session_maker() as session:

            get_booked_rooms = select(
                self.model.id,
                func.count().label("booked_rooms")
            ).select_from(self.model).join(
                self.model,
                Bookings.room_id == self.model.id
            ).where(
                (Bookings.date_from <= date_to) &
                (Bookings.date_to >= date_from)
            ).group_by(self.model.id).subquery("booked_rooms")

            get_available_rooms = select(
                self.model.id,
                self.model.hotel_id,
                self.model.name,
                self.model.description,
                self.model.services,
                self.model.price,
                self.model.quantity,
                self.model.image_id,
                (self.model.price * (date_to - date_from).days).label("total_cost"),
                (self.model.quantity - func.coalesce(get_booked_rooms.c.booked_rooms, 0)).label("rooms_left")
            ).select_from(self.model).outerjoin(
                get_booked_rooms,
                self.model.id == get_booked_rooms.c.id
            ).where(self.model.hotel_id == hotel_id)

            available_rooms = await session.execute(get_available_rooms)

            return available_rooms.mappings().all()

