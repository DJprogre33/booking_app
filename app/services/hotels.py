import os
import shutil
import uuid
from datetime import date
from typing import Optional

from fastapi import Request, UploadFile

# from app.auth.auth import get_current_user, get_token
from app.exceptions import AccessDeniedException, IncorrectHotelIDException
from app.logger import logger
from app.models.hotels import Hotels
from app.repositories.hotels import HotelsRepository
from app.schemas.hotels import SHotel, SHotelsResponse
from app.utils.base import Base


class HotelsService:
    tasks_repo: HotelsRepository = HotelsRepository

    @classmethod
    async def check_hotel_owner(cls, hotel_id: int, owner_id: int) -> Hotels:
        hotel = await cls.tasks_repo.find_one_or_none(id=hotel_id)
        if not hotel:
            logger.warning("Incorrect hotel id", extra={"hotel_id": hotel_id})
            raise IncorrectHotelIDException
        if hotel.owner_id != owner_id:
            logger.warning(
                "User isn't an owner", extra={"hotel_id": hotel_id, "user_id": owner_id}
            )
            raise AccessDeniedException
        return hotel

    @classmethod
    async def create_hotel(
            cls,
            name: str,
            location: str,
            services: list,
            rooms_quantity: int,
            owner_id: int
    ) -> Hotels:
        return await cls.tasks_repo.insert_data(
            name=name,
            location=location,
            services=services,
            rooms_quantity=rooms_quantity,
            owner_id=owner_id,
        )

    @classmethod
    async def update_hotel(
            cls,
            hotel_id: int,
            name: str,
            location: str,
            services: list,
            rooms_quantity: int,
            owner_id: int
    ) -> Hotels:
        hotel = await cls.check_hotel_owner(hotel_id=hotel_id, owner_id=owner_id)
        return await cls.tasks_repo.update_fields_by_id(
            entity_id=hotel.id,
            name=name,
            location=location,
            services=services,
            rooms_quantity=rooms_quantity,
            owner_id=owner_id,
        )

    @classmethod
    async def add_hotel_image(
        cls, hotel_id: int, hotel_image: UploadFile, owner_id: int
    ) -> Hotels:
        hotel = await cls.check_hotel_owner(hotel_id=hotel_id, owner_id=owner_id)
        if hotel.image_path:
            os.remove(hotel.image_path)

        hotel_image.filename = str(uuid.uuid4())
        file_path = f"app/static/images/hotels/{hotel_image.filename}.webp"
        with open(file_path, "wb") as file:
            shutil.copyfileobj(hotel_image.file, file)
        return await cls.tasks_repo.update_fields_by_id(hotel_id, image_path=file_path)

    @classmethod
    async def delete_hotel_image(cls, hotel_id: int, owner_id: int) -> Hotels:
        hotel = await cls.check_hotel_owner(hotel_id=hotel_id, owner_id=owner_id)
        if hotel.image_path:
            os.remove(hotel.image_path)
        return await cls.tasks_repo.update_fields_by_id(hotel_id, image_path="")

    @classmethod
    async def delete_hotel(cls, hotel_id: int, owner_id: int) -> Hotels:
        hotel = await cls.check_hotel_owner(hotel_id=hotel_id, owner_id=owner_id)
        return await cls.tasks_repo.delete(id=hotel.id)

    @classmethod
    async def get_hotels_by_location_and_time(
        cls, location: str, date_from: date, date_to: date
    ) -> Optional[list[SHotelsResponse]]:
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        return await cls.tasks_repo.get_hotels_by_location_and_time(
            location=location, date_from=date_from, date_to=date_to
        )

    @classmethod
    async def get_hotel_by_id(cls, hotel_id: int) -> Hotels:
        hotel = await cls.tasks_repo.find_one_or_none(id=hotel_id)
        if not hotel:
            raise IncorrectHotelIDException
        return hotel
