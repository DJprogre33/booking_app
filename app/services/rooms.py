from datetime import date

from app.repositories.rooms import RoomsRepository
from app.utils.base import Base


class RoomsService:
    def __init__(self, tasks_repo: RoomsRepository):
        self.task_repo: RoomsRepository = tasks_repo()

    async def get_availible_hotel_rooms(
            self,
            hotel_id: int,
            date_from: date,
            date_to: date
    ):
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        return await self.task_repo.get_available_hotel_rooms(
            hotel_id=hotel_id,
            date_from=date_from,
            date_to=date_to
        )
