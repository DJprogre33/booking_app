import os
import shutil
import uuid
from asyncio import sleep
from datetime import date

from fastapi import APIRouter, Depends, UploadFile
from fastapi_cache.decorator import cache
from fastapi_versioning import version

from app.dependencies import check_owner, get_current_user, validate_data_range
from app.exceptions import AccessDeniedException, IncorrectHotelIDException
from app.hotels.dao import HotelDAO
from app.hotels.models import Hotels
from app.hotels.schemas import SHotel, SHotelResponse, SHotelsResponse
from app.logger import logger
from app.users.models import Users


router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("/{location}", response_model=list[SHotelsResponse])
@cache(expire=60)
@version(1)
async def get_hotels_by_location_and_time(
    location: str,
    date_from: date,
    date_to: date,
    validated_dates: tuple = Depends(validate_data_range),
):
    date_from, date_to = validated_dates
    await sleep(3)
    return await HotelDAO.get_hotels_with_available_rooms_by_location(
        location, date_from, date_to
    )


@router.get("/id/{hotel_id}", response_model=SHotelResponse)
@version(1)
async def get_hotel_by_id(hotel_id: int):
    return await HotelDAO.find_one_or_none(id=hotel_id)


@router.post("/new")
async def create_hotel(new_hotel: SHotel, user=Depends(get_current_user)):
    if user.role != "hotel owner":
        logger.warning("Role access denied", extra={"user_id": user.id})
        raise AccessDeniedException()

    new_hotel_id = await HotelDAO.insert_data(
        name=new_hotel.name,
        location=new_hotel.location,
        services=new_hotel.services,
        rooms_quantity=new_hotel.rooms_quantity,
        owner_id=user.id,
    )
    logger.info("Succesful created a new hotel", extra={"new_hotel_id": new_hotel_id})

    return {"new_hotel_id": new_hotel_id}


@router.patch("/{hotel_id}/image", response_model=SHotelResponse)
async def add_hotel_image(
    hotel_id: int,
    hotel_image: UploadFile,
    user=Depends(get_current_user),
    hotel=Depends(check_owner),
):
    if hotel.image_path:
        os.remove(hotel.image_path)

    hotel_image.filename = str(uuid.uuid4())
    file_path = f"app/static/images/hotels/{hotel_image.filename}.webp"

    with open(file_path, "wb") as file:
        shutil.copyfileobj(hotel_image.file, file)

    result = await HotelDAO.update_fields_by_id(hotel_id, image_path=file_path)
    logger.info(
        "Succesfully uploaded a hotel image", extra={"image_path": result.image_path}
    )
    return result


@router.delete("/{hotel_id}/image", response_model=None)
async def delete_hotel_image(
    hotel_id: int,
    user = Depends(get_current_user),
    hotel = Depends(check_owner),
):
    if hotel.image_path:
        os.remove(hotel.image_path)

    return {"deleted_image_path": hotel.image_path}
