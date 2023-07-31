import os
import shutil
import uuid
from datetime import date

from fastapi import Request, UploadFile

from app.auth.auth import get_current_user, get_token
from app.exceptions import AccessDeniedException, IncorrectHotelIDException
from app.logger import logger
from app.repositories.hotels import HotelsRepository
from app.schemas.hotels import SHotel
from app.utils.base import Base


class HotelsService:
    tasks_repo: HotelsRepository = HotelsRepository

    @classmethod
    async def get_hotels_by_location_and_time(
        cls, location: str, date_from: date, date_to: date
    ):
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        return await cls.tasks_repo.get_hotels_by_location_and_time(
            location=location, date_from=date_from, date_to=date_to
        )

    @classmethod
    async def get_hotel_by_id(cls, hotel_id: int):
        hotel = await cls.tasks_repo.find_one_or_none(id=hotel_id)
        if not hotel:
            raise IncorrectHotelIDException()
        return hotel

    @classmethod
    async def create_hotel(cls, new_hotel: SHotel, request: Request):
        token = get_token(request)
        user = await get_current_user(token)
        if user.role != "hotel owner":
            logger.warning("Role access denied", extra={"user_id": user.id})
            raise AccessDeniedException()

        return await cls.tasks_repo.insert_data(
            name=new_hotel.name,
            location=new_hotel.location,
            services=new_hotel.services,
            rooms_quantity=new_hotel.rooms_quantity,
            owner_id=user.id,
        )

    @classmethod
    async def delete_hotel(cls, hotel_id: int, request: Request):
        token = get_token(request)
        user = await get_current_user(token)
        hotel = await Base.check_owner(
            task_repo=cls.tasks_repo, hotel_id=hotel_id, user_id=user.id
        )

        return await cls.tasks_repo.delete_by_id(hotel.id)

    @classmethod
    async def add_hotel_image(
        cls, hotel_id: int, request: Request, hotel_image: UploadFile
    ):
        token = get_token(request)
        user = await get_current_user(token)
        hotel = await Base.check_owner(
            task_repo=cls.tasks_repo, hotel_id=hotel_id, user_id=user.id
        )

        if hotel.image_path:
            os.remove(hotel.image_path)

        hotel_image.filename = str(uuid.uuid4())
        file_path = f"app/static/images/hotels/{hotel_image.filename}.webp"

        with open(file_path, "wb") as file:
            shutil.copyfileobj(hotel_image.file, file)

        return await cls.tasks_repo.update_fields_by_id(hotel_id, image_path=file_path)

    @classmethod
    async def delete_hotel_image(cls, hotel_id: int, request: Request):
        token = get_token(request)
        user = await get_current_user(token)
        hotel = await Base.check_owner(
            task_repo=cls.tasks_repo, hotel_id=hotel_id, user_id=user.id
        )

        if hotel.image_path:
            os.remove(hotel.image_path)

        return await cls.tasks_repo.update_fields_by_id(hotel_id, image_path="")
