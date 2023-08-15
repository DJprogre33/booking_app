import os
import shutil
import uuid
from datetime import date
from typing import Optional

from fastapi import UploadFile

from app.exceptions import IncorrectRoomIDException, RoomLimitExceedException
from app.logger import logger
from app.models.rooms import Rooms
from app.schemas.rooms import SRoomResponse
from app.services.hotels import HotelsService
from app.utils.base import Base
from app.utils.transaction_manager import ITransactionManager


class RoomsService:

    @staticmethod
    async def create_room(
        transaction_manager: ITransactionManager,
        hotel_id: int,
        name: str,
        description: str,
        price: int,
        services: list,
        quantity: int,
        owner_id: int
    ) -> Rooms:
        async with transaction_manager:
            hotel = await HotelsService().check_hotel_owner(
                transaction_manager=transaction_manager,
                hotel_id=hotel_id,
                owner_id=owner_id
            )
            rooms_left = await transaction_manager.rooms.get_rooms_left(hotel_id=hotel.id)

            if rooms_left >= quantity:
                new_room = await transaction_manager.rooms.insert_data(
                    hotel_id=hotel.id,
                    name=name,
                    description=description,
                    price=price,
                    services=services,
                    quantity=quantity,
                )
                await transaction_manager.commit()
                return new_room
            logger.warning(
                "The number of rooms exceeds the total number of rooms in the hotel",
                extra={"rooms_left": rooms_left, "required quantity": quantity},
            )
            raise RoomLimitExceedException

    @staticmethod
    async def update_room(
        transaction_manager: ITransactionManager,
        hotel_id: int,
        room_id: int,
        name: str,
        description: str,
        price: int,
        services: list,
        quantity: int,
        owner_id: int
    ) -> Rooms:
        hotel = await HotelsService().check_hotel_owner(
            transaction_manager=transaction_manager,
            hotel_id=hotel_id,
            owner_id=owner_id
        )
        async with transaction_manager:
            room = await transaction_manager.rooms.find_one_or_none(id=room_id, hotel_id=hotel_id)
            if not room:
                logger.warning(
                    "Incorrect hotel_id or room_id",
                    extra={"hotel_id": hotel.id, "room_id": room_id},
                )
                raise IncorrectRoomIDException

            rooms_left = await transaction_manager.rooms.get_rooms_left(hotel_id=hotel.id)
            if rooms_left + room.quantity >= quantity:
                updated_room = await transaction_manager.rooms.update_fields_by_id(
                    entity_id=room.id,
                    hotel_id=hotel.id,
                    name=name,
                    description=description,
                    price=price,
                    services=services,
                    quantity=quantity,
                )
                await transaction_manager.commit()
                return updated_room
            logger.warning(
                "The number of rooms exceeds the total number of rooms in the hotel",
                extra={"rooms_left": rooms_left, "required quantity": quantity},
            )
            raise RoomLimitExceedException

    @staticmethod
    async def delete_room(
        transaction_manager: ITransactionManager,
        hotel_id: int,
        room_id: int,
        owner_id: int
    ) -> Rooms:
        async with transaction_manager:
            hotel = await HotelsService().check_hotel_owner(
                transaction_manager=transaction_manager,
                hotel_id=hotel_id,
                owner_id=owner_id
            )
            room = await transaction_manager.rooms.find_one_or_none(id=room_id, hotel_id=hotel.id)
            if not room:
                logger.warning(
                    "Incorrect hotel_id or room_id",
                    extra={"hotel_id": hotel.id, "room_id": room_id},
                )
                raise IncorrectRoomIDException
            deleted_room = await transaction_manager.rooms.delete(id=room.id, hotel_id=hotel.id)
            await transaction_manager.commit()
            return deleted_room

    @staticmethod
    async def add_room_image(
            transaction_manager: ITransactionManager,
            hotel_id: int,
            room_id: int,
            room_image: UploadFile,
            owner_id: int
    ) -> Rooms:
        hotel = await HotelsService().check_hotel_owner(
            transaction_manager=transaction_manager,
            hotel_id=hotel_id,
            owner_id=owner_id
        )
        async with transaction_manager:
            room = await transaction_manager.rooms.find_one_or_none(id=room_id, hotel_id=hotel.id)
            if not room:
                logger.warning(
                    "Incorrect hotel_id or room_id",
                    extra={"hotel_id": hotel.id, "room_id": room_id},
                )
                raise IncorrectRoomIDException

            if room.image_path:
                os.remove(room.image_path)
            room_image.filename = str(uuid.uuid4())
            file_path = f"app/static/images/rooms/{room_image.filename}.webp"

            with open(file_path, "wb") as file:
                shutil.copyfileobj(room_image.file, file)
            updated_room = await transaction_manager.rooms.update_fields_by_id(
                entity_id=room_id, image_path=file_path
            )
            await transaction_manager.commit()
            return updated_room

    @staticmethod
    async def delete_room_image(
        transaction_manager: ITransactionManager,
        hotel_id: int,
        room_id: int,
        owner_id: int
    ) -> Rooms:
        async with transaction_manager:
            hotel = await HotelsService().check_hotel_owner(
                transaction_manager=transaction_manager,
                hotel_id=hotel_id,
                owner_id=owner_id
            )
            room = await transaction_manager.rooms.find_one_or_none(id=room_id, hotel_id=hotel.id)
            if not room:
                logger.warning(
                    "Incorrect hotel_id or room_id",
                    extra={"hotel_id": hotel.id, "room_id": room_id},
                )
                raise IncorrectRoomIDException
            if room.image_path:
                os.remove(room.image_path)
            updated_room = await transaction_manager.rooms.update_fields_by_id(
                entity_id=room_id, image_path=""
            )
            await transaction_manager.commit()
            return updated_room

    @staticmethod
    async def get_availible_hotel_rooms(
        transaction_manager: ITransactionManager,
        hotel_id: int,
        date_from: date,
        date_to: date
    ) -> Optional[list[SRoomResponse]]:
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        async with transaction_manager:
            hotel = await HotelsService().get_hotel_by_id(
                transaction_manager=transaction_manager,
                hotel_id=hotel_id
            )
            rooms = await transaction_manager.rooms.get_available_hotel_rooms(
                hotel_id=hotel.id, date_from=date_from, date_to=date_to
            )
            await transaction_manager.commit()
            return rooms

    @staticmethod
    async def get_room(transaction_manager: ITransactionManager, room_id: int) -> Rooms:
        async with transaction_manager:
            room = await transaction_manager.rooms.find_one_or_none(id=room_id)
            if not room:
                logger.warning("Incorrect room_id", extra={"room_id": room_id})
                raise IncorrectRoomIDException
            await transaction_manager.commit()
            return room
