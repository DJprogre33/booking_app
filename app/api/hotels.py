from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi_cache.decorator import cache
from fastapi_versioning import version

from app.dependencies import get_hotels_service
from app.logger import logger
from app.schemas.hotels import SHotel, SHotelResponse, SHotelsResponse
from app.exceptions import SExstraResponse
from app.services.hotels import HotelsService
from app.dependencies import get_current_user, get_current_hotel_owner
from app.models.users import Users

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.post(
    "/new",
    response_model=SHotelResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse}
    }
)
@version(1)
async def create_hotel(
    new_hotel: SHotel,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
    current_user: Users = Depends(get_current_hotel_owner)
):
    """Creates a hotel if the user has the hotel_owner role"""
    new_hotel = await tasks_service.create_hotel(new_hotel=new_hotel, owner_id=current_user.id)
    logger.info("Succesful created a new hotel", extra={"new_hotel_id": new_hotel.id})
    return new_hotel


@router.patch(
    "/{hotel_id}/image",
    response_model=SHotelResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse}
    }
)
@version(1)
async def add_hotel_image(
    hotel_id: int,
    hotel_image: UploadFile,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
    current_user: Users = Depends(get_current_hotel_owner)
):
    """Adds an image for the created hotel, current user must be a hotel owner"""
    result = await tasks_service.add_hotel_image(
        hotel_id=hotel_id, hotel_image=hotel_image, owner_id=current_user.id
    )
    logger.info(
        "Succesfully uploaded a hotel image", extra={"image_path": result.image_path}
    )
    return result


@router.delete(
    "/{hotel_id}/image",
    response_model=SHotelResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse}
    }
)
@version(1)
async def delete_hotel_image(
    hotel_id: int,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
    current_user: Users = Depends(get_current_hotel_owner)
):
    """Deletes the image for a hotel by id, current user must be a hotel owner"""
    hotel = await tasks_service.delete_hotel_image(
        hotel_id=hotel_id, owner_id=current_user.id
    )
    logger.info(
        "Succesfully deleted a hotel image",
        extra={"hotel_with_deleted_image_id": hotel.id},
    )
    return hotel


@router.delete(
    "/{hotel_id}",
    response_model=SHotelResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse}
    }
)
@version(1)
async def delete_hotel(
    hotel_id: int,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
    current_user: Users = Depends(get_current_hotel_owner)
):
    """Deletes a hotel by id if the user is the owner of the hotel"""
    hotel = await tasks_service.delete_hotel(
        hotel_id=hotel_id, owner_id=current_user.id
    )
    logger.info(
        "Succesfully deleted hotel", extra={"deleted_hotel_id": hotel}
    )
    return hotel


@router.get(
    "/{location}",
    response_model=Optional[list[SHotelsResponse]],
    responses={
        400: {"model": SExstraResponse}
    }
)
@cache(expire=60)
@version(1)
async def get_hotels_by_location_and_time(
    location: str,
    date_from: date,
    date_to: date,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
):
    """Gives a list of hotels with free rooms for a certain date"""
    hotels = await tasks_service.get_hotels_by_location_and_time(
        location=location, date_from=date_from, date_to=date_to
    )
    logger.info("Succesful return hotels")
    return hotels


@router.get(
    "/id/{hotel_id}",
    response_model=SHotelResponse,
    responses={
        404: {"model": SExstraResponse}
    }
)
@version(1)
@cache(expire=60)
async def get_hotel_by_id(
    hotel_id: int, tasks_service: Annotated[HotelsService, Depends(get_hotels_service)]
):
    """Returns the hotel by id"""
    hotel = await tasks_service.get_hotel_by_id(hotel_id=hotel_id)
    logger.info(
        "Succesfully return a hotel", extra={"hotel_id": hotel.id}
    )
    return hotel
