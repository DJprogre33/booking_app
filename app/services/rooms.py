from datetime import date
import os
import uuid
import shutil

from app.repositories.rooms import RoomsRepository
from app.utils.base import Base
from app.auth.auth import get_current_user
from app.repositories.hotels import HotelsRepository
from app.logger import logger
from app.exceptions import RoomLimitExceedException, IncorrectRoomIDException
from fastapi import Request, UploadFile


class RoomsService:
    def __init__(self, tasks_repo: RoomsRepository):
        self.tasks_repo: RoomsRepository = tasks_repo()

    async def get_availible_hotel_rooms(
            self,
            hotel_id: int,
            date_from: date,
            date_to: date
    ):
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        return await self.tasks_repo.get_available_hotel_rooms(
            hotel_id=hotel_id,
            date_from=date_from,
            date_to=date_to
        )

    async def create_room(
        self,
        hotel_id: int,
        name: str,
        description: str,
        price: int,
        services: list,
        quantity: int,
        request: Request
    ) -> dict:
        user = await get_current_user(request)
        hotel = await Base.check_owner(task_repo=HotelsRepository(), hotel_id=hotel_id, user_id=user.id)

        rooms_left = await self.tasks_repo.get_rooms_left(hotel_id=hotel.id)

        if rooms_left >= quantity:
            return await self.tasks_repo.insert_data(
                hotel_id=hotel.id,
                name=name,
                description=description,
                price=price,
                services=services,
                quantity=quantity
            )

        logger.warning(
            "The number of rooms exceeds the total number of rooms in the hotel",
            extra={"rooms_left": rooms_left, "required quantity": quantity}
        )
        raise RoomLimitExceedException()

    async def delete_room(
        self,
        hotel_id: int,
        room_id: int,
        request: Request
    ) -> id:
        user = await get_current_user(request)
        await Base.check_owner(task_repo=HotelsRepository(), hotel_id=hotel_id, user_id=user.id)

        return await self.tasks_repo.delete_by_id(room_id)

    async def add_room_image(
        self,
        hotel_id: int,
        room_id: int,
        room_image: UploadFile,
        request: Request
    ):
        user = await get_current_user(request)
        await Base.check_owner(task_repo=HotelsRepository(), hotel_id=hotel_id, user_id=user.id)
        room = await self.tasks_repo.find_one_or_none(id=room_id)

        if not room:
            raise IncorrectRoomIDException()

        if room.image_path:
            os.remove(room.image_path)

        room_image.filename = str(uuid.uuid4())
        file_path = f"app/static/images/rooms/{room_image.filename}.webp"

        with open(file_path, "wb") as file:
            shutil.copyfileobj(room_image.file, file)

        return await self.tasks_repo.update_fields_by_id(entity_id=room_id, image_path=file_path)

    async def delete_room_image(
        self,
        hotel_id: int,
        room_id: int,
        request: Request
    ):
        user = await get_current_user(request)
        await Base.check_owner(task_repo=HotelsRepository(), hotel_id=hotel_id, user_id=user.id)
        room = await self.tasks_repo.find_one_or_none(id=room_id)

        if not room:
            raise IncorrectRoomIDException()

        if room.image_path:
            os.remove(room.image_path)

        return await self.tasks_repo.update_fields_by_id(entity_id=room_id, image_path="")