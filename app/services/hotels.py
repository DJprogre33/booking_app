import os
import shutil
import uuid
from datetime import date

from fastapi import Depends, UploadFile

from app.dependencies import get_current_user
from app.exceptions import AccessDeniedException, IncorrectHotelIDException
from app.logger import logger
from app.models.hotels import Hotels
from app.repositories.hotels import HotelsRepository
from app.schemas.hotels import SHotel
from app.utils.base import Base


class HotelsService:
    def __init__(self, tasks_repo: HotelsRepository):
        self.tasks_repo: HotelsRepository = tasks_repo()

    async def get_hotels_by_location_and_time(
            self,
            location: str,
            date_from: date,
            date_to: date
    ):
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        return await self.tasks_repo.get_hotels_by_location_and_time(
            location=location,
            date_from=date_from,
            date_to=date_to
        )

    async def get_hotel_by_id(self, hotel_id: int):
        return await self.tasks_repo.find_one_or_none(id=hotel_id)

    async def create_hotel(
            self,
            new_hotel: SHotel,
            user=Depends(get_current_user)
    ):
        if user.role != "hotel owner":
            logger.warning("Role access denied", extra={"user_id": user.id})
            raise AccessDeniedException()

        return await self.tasks_repo.insert_data(
            name=new_hotel.name,
            location=new_hotel.location,
            services=new_hotel.services,
            rooms_quantity=new_hotel.rooms_quantity,
            owner_id=user.id
        )

    async def check_owner(self, hotel_id: int, user=Depends(get_current_user)) -> Hotels:

        hotel = await self.tasks_repo.find_one_or_none(id=hotel_id)

        if not hotel:
            logger.warning("Incorrect hotel id", extra={"hotel_id": hotel_id})
            raise IncorrectHotelIDException()

        if hotel.owner_id != user.id:
            logger.warning("User isn't an owner", extra={"hotel_id": hotel_id, "user_id": user.id})
            raise AccessDeniedException()

        return hotel

    async def add_hotel_image(
            self,
            hotel_id: int,
            hotel_image: UploadFile
    ):
        hotel = await self.check_owner(hotel_id)

        if hotel.image_path:
            os.remove(hotel.image_path)

        hotel_image.filename = str(uuid.uuid4())
        file_path = f"app/static/images/hotels/{hotel_image.filename}.webp"

        with open(file_path, "wb") as file:
            shutil.copyfileobj(hotel_image.file, file)

        return await self.tasks_repo.update_fields_by_id(hotel_id, image_path=file_path)

    async def delete_hotel_image(self, hotel_id: int):
        hotel = await self.check_owner(hotel_id)

        if hotel.image_path:
            os.remove(hotel.image_path)

        hotel = await self.tasks_repo.update_fields_by_id(hotel_id, image_path="")

        return hotel.id
