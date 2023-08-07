import os
import shutil
import uuid
from datetime import date

from fastapi import Request, UploadFile

# from app.auth.auth import get_current_user, get_token
from app.exceptions import IncorrectRoomIDException, RoomLimitExceedException
from app.logger import logger
from app.models.rooms import Rooms
from app.repositories.hotels import HotelsRepository
from app.repositories.rooms import RoomsRepository
from app.utils.base import Base


class RoomsService:
    tasks_repo: RoomsRepository = RoomsRepository
    
    @classmethod
    async def get_availible_hotel_rooms(
        cls, hotel_id: int, date_from: date, date_to: date
    ):
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        return await cls.tasks_repo.get_available_hotel_rooms(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
    
    @classmethod
    async def create_room(
        cls,
        hotel_id: int,
        name: str,
        description: str,
        price: int,
        services: list,
        quantity: int,
        request: Request,
    ) -> Rooms:
        token = get_token(request)
        user = await get_current_user(token)
        hotel = await Base.check_owner(
            task_repo=HotelsRepository(), hotel_id=hotel_id, user_id=user.id
        )

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
        raise RoomLimitExceedException()
    
    @classmethod
    async def delete_room(cls, hotel_id: int, room_id: int, request: Request) -> id:
        token = get_token(request)
        user = await get_current_user(token)
        await Base.check_owner(
            task_repo=HotelsRepository(), hotel_id=hotel_id, user_id=user.id
        )

        return await cls.tasks_repo.delete(id=room_id)
    
    @classmethod
    async def add_room_image(
        cls, hotel_id: int, room_id: int, room_image: UploadFile, request: Request
    ):
        token = get_token(request)
        user = await get_current_user(token)
        await Base.check_owner(
            task_repo=HotelsRepository(), hotel_id=hotel_id, user_id=user.id
        )
        room = await cls.tasks_repo.find_one_or_none(id=room_id)

        if not room:
            raise IncorrectRoomIDException()

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
    async def delete_room_image(cls, hotel_id: int, room_id: int, request: Request):
        token = get_token(request)
        user = await get_current_user(token)
        await Base.check_owner(
            task_repo=HotelsRepository(), hotel_id=hotel_id, user_id=user.id
        )
        room = await cls.tasks_repo.find_one_or_none(id=room_id)

        if not room:
            raise IncorrectRoomIDException()

        if room.image_path:
            os.remove(room.image_path)

        return await cls.tasks_repo.update_fields_by_id(
            entity_id=room_id, image_path=""
        )
