import os
import shutil
import uuid
from datetime import date
from typing import Optional

from fastapi import UploadFile

from app.exceptions import AccessDeniedException, IncorrectHotelIDException
from app.logger import logger
from app.models.hotels import Hotels
from app.schemas.hotels import SHotelsResponse
from app.utils.base import Base
from app.utils.transaction_manager import ITransactionManager


class HotelsService:

    @staticmethod
    async def check_hotel_owner(
        transaction_manager: ITransactionManager, hotel_id: int, owner_id: int
    ) -> Hotels:
        async with transaction_manager:
            hotel = await transaction_manager.hotels.find_one_or_none(id=hotel_id)
            if not hotel:
                logger.warning("Incorrect hotel id", extra={"hotel_id": hotel_id})
                raise IncorrectHotelIDException
            if hotel.owner_id != owner_id:
                logger.warning(
                    "User isn't an owner",
                    extra={"hotel_id": hotel_id, "user_id": owner_id},
                )
                raise AccessDeniedException
            await transaction_manager.commit()
            return hotel

    @staticmethod
    async def create_hotel(
        transaction_manager: ITransactionManager,
        name: str,
        location: str,
        services: list,
        rooms_quantity: int,
        owner_id: int,
    ) -> Hotels:
        async with transaction_manager:
            new_hotel = await transaction_manager.hotels.insert_data(
                name=name,
                location=location,
                services=services,
                rooms_quantity=rooms_quantity,
                owner_id=owner_id,
            )
            await transaction_manager.commit()
            return new_hotel

    async def update_hotel(
        self,
        transaction_manager: ITransactionManager,
        hotel_id: int,
        name: str,
        location: str,
        services: list,
        rooms_quantity: int,
        owner_id: int,
    ) -> Hotels:
        async with transaction_manager:
            current_hotel = await self.check_hotel_owner(
                transaction_manager=transaction_manager,
                hotel_id=hotel_id,
                owner_id=owner_id,
            )
            updated_hotel = await transaction_manager.hotels.update_fields_by_id(
                entity_id=current_hotel.id,
                name=name,
                location=location,
                services=services,
                rooms_quantity=rooms_quantity,
                owner_id=owner_id,
            )
            await transaction_manager.commit()
            return updated_hotel

    async def add_hotel_image(
        self,
        transaction_manager: ITransactionManager,
        hotel_id: int,
        hotel_image: UploadFile,
        owner_id: int,
    ) -> Hotels:
        async with transaction_manager:
            current_hotel = await self.check_hotel_owner(
                transaction_manager=transaction_manager,
                hotel_id=hotel_id,
                owner_id=owner_id,
            )
            if current_hotel.image_path:
                os.remove(current_hotel.image_path)

            hotel_image.filename = str(uuid.uuid4())
            file_path = f"app/static/images/hotels/{hotel_image.filename}.webp"
            with open(file_path, "wb") as file:
                shutil.copyfileobj(hotel_image.file, file)
            updated_hotel = await transaction_manager.hotels.update_fields_by_id(
                hotel_id, image_path=file_path
            )
            await transaction_manager.commit()
            return updated_hotel

    async def delete_hotel_image(
        self, transaction_manager: ITransactionManager, hotel_id: int, owner_id: int
    ) -> Hotels:
        async with transaction_manager:
            current_hotel = await self.check_hotel_owner(
                transaction_manager=transaction_manager,
                hotel_id=hotel_id,
                owner_id=owner_id,
            )
            if current_hotel.image_path:
                os.remove(current_hotel.image_path)
            updated_hotel = await transaction_manager.hotels.update_fields_by_id(
                hotel_id, image_path=""
            )
            await transaction_manager.commit()
            return updated_hotel

    async def delete_hotel(
        self, transaction_manager: ITransactionManager, hotel_id: int, owner_id: int
    ) -> Hotels:
        async with transaction_manager:
            current_hotel = await self.check_hotel_owner(
                transaction_manager=transaction_manager,
                hotel_id=hotel_id,
                owner_id=owner_id,
            )
            deleted_hotel = await transaction_manager.hotels.delete(id=current_hotel.id)
            await transaction_manager.commit()
            return deleted_hotel

    @staticmethod
    async def get_hotels_by_location_and_time(
        transaction_manager: ITransactionManager,
        location: str,
        date_from: date,
        date_to: date,
    ) -> Optional[list[SHotelsResponse]]:
        date_from, date_to = Base.validate_data_range(date_from, date_to)
        async with transaction_manager:
            hotels = await transaction_manager.hotels.get_hotels_by_location_and_time(
                location=location, date_from=date_from, date_to=date_to
            )
            await transaction_manager.commit()
            return hotels

    @staticmethod
    async def get_hotel_by_id(
        transaction_manager: ITransactionManager, hotel_id: int
    ) -> Hotels:
        async with transaction_manager:
            hotel = await transaction_manager.hotels.find_one_or_none(id=hotel_id)
            if not hotel:
                raise IncorrectHotelIDException
            await transaction_manager.commit()
            return hotel
