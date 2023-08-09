import os
import shutil
import uuid
from datetime import date
from typing import Optional
from fastapi import UploadFile

from app.exceptions import IncorrectRoomIDException, RoomLimitExceedException
from app.logger import logger
from app.models.rooms import Rooms
from app.repositories.rooms import RoomsRepository
from app.utils.base import Base
from app.services.hotels import HotelsService
from app.schemas.hotels import SHotelsResponse

class RoomsService:
    tasks_repo: RoomsRepository = RoomsRepository

    @classmethod
    async def create_room(
            cls,
            hotel_id: int,
            name: str,
            description: str,
            price: int,
            services: list,
            quantity: int,
            owner_id: int
    ) -> Rooms:
        hotel = await HotelsService.check_hotel_owner(hotel_id=hotel_id, owner_id=owner_id)
        rooms_left = await cls.tasks_repo.get_rooms_left(hotel_id=hotel.id)

        if rooms_left >= quantity:
            return await cls.tasks_repo.insert_data(
                hotel_id=hotel.id,
                name=name,
                description=description,
                price=price,
                services=services,
                quantity=quantity,
            )
        logger.warning(
            "The number of rooms exceeds the total number of rooms in the hotel",
            extra={"rooms_left": rooms_left, "required quantity": quantity},
        )
        raise RoomLimitExceedException

    @classmethod
    async def update_room(
            cls,
            hotel_id: int,
            room_id: int,
            name: str,
            description: str,
            price: int,
            services: list,
            quantity: int,
            owner_id: int
    ) -> Rooms:
        hotel = await HotelsService.check_hotel_owner(hotel_id=hotel_id, owner_id=owner_id)
        room = await cls.tasks_repo.find_one_or_none(id=room_id)
        if not room:
            raise IncorrectRoomIDException

        rooms_left = await cls.tasks_repo.get_rooms_left(hotel_id=hotel.id)
        if rooms_left + room.quantity >= quantity:
            return await cls.tasks_repo.update_fields_by_id(
                entity_id=room.id,
                hotel_id=hotel.id,
                name=name,
                description=description,
                price=price,
                services=services,
                quantity=quantity,
            )
        logger.warning(
            "The number of rooms exceeds the total number of rooms in the hotel",
            extra={"rooms_left": rooms_left, "required quantity": quantity},
        )
        raise RoomLimitExceedException

    @classmethod
    async def delete_room(cls, hotel_id: int, room_id: int, owner_id: int) -> Rooms:
        hotel = await HotelsService.check_hotel_owner(hotel_id=hotel_id, owner_id=owner_id)
        room = await cls.tasks_repo.find_one_or_none(id=room_id)
        if not room:
            raise IncorrectRoomIDException
        return await cls.tasks_repo.delete(id=room.id, hotel_id=hotel.id)

    @classmethod
    async def add_room_image(
            cls, hotel_id: int, room_id: int, room_image: UploadFile, owner_id: int
    ) -> Rooms:
        hotel = await HotelsService.check_hotel_owner(hotel_id=hotel_id, owner_id=owner_id)
        room = await cls.tasks_repo.find_one_or_none(id=room_id, hotel_id=hotel.id)
        if not room:
            raise IncorrectRoomIDException
        if room.image_path:
            os.remove(room.image_path)
        room_image.filename = str(uuid.uuid4())
        file_path = f"app/static/images/rooms/{room_image.filename}.webp"
        with open(file_path, "wb") as file:
            shutil.copyfileobj(room_image.file, file)
        return await cls.tasks_repo.update_fields_by_id(
            entity_id=room_id, image_path=file_path
        )

    @classmethod
    async def delete_room_image(cls, hotel_id: int, room_id: int, owner_id: int) -> Rooms:
        hotel = await HotelsService.check_hotel_owner(hotel_id=hotel_id, owner_id=owner_id)
        room = await cls.tasks_repo.find_one_or_none(id=room_id, hotel_id=hotel.id)
        if not room:
            raise IncorrectRoomIDException
        if room.image_path:
            os.remove(room.image_path)
        return await cls.tasks_repo.update_fields_by_id(
            entity_id=room_id, image_path=""
        )

    @classmethod
    async def get_availible_hotel_rooms(
        cls, hotel_id: int, date_from: date, date_to: date
    ) -> Optional[list[SHotelsResponse]]:
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        hotel = await HotelsService.get_hotel_by_id(hotel_id=hotel_id)
        return await cls.tasks_repo.get_available_hotel_rooms(
            hotel_id=hotel.id, date_from=date_from, date_to=date_to
        )
