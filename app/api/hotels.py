from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile
from fastapi_cache.decorator import cache
from fastapi_versioning import version

from app.dependencies import TManagerDep, get_current_hotel_owner
from app.exceptions import SExstraResponse
from app.logger import logger
from app.models.users import Users
from app.schemas.hotels import SHotel, SHotelResponse, SHotelsResponse
from app.services.hotels import HotelsService

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.post(
    "/new",
    response_model=SHotelResponse,
    responses={401: {"model": SExstraResponse}, 403: {"model": SExstraResponse}},
)
@version(1)
async def create_hotel(
    new_hotel: SHotel,
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_hotel_owner),
):
    """Creates a hotel if the user has the hotel_owner role"""
    new_hotel = await HotelsService().create_hotel(
        transaction_manager=transaction_manager,
        name=new_hotel.name,
        location=new_hotel.location,
        services=new_hotel.services,
        rooms_quantity=new_hotel.rooms_quantity,
        owner_id=current_user.id,
    )
    logger.info("Succesful created a new hotel", extra={"new_hotel_id": new_hotel.id})
    return new_hotel


@router.put(
    "/{hotel_id}",
    response_model=SHotelResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse},
    },
)
@version(1)
async def update_hotel(
    hotel_id: int,
    new_hotel: SHotel,
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_hotel_owner),
):
    """Updates a hotel if the user has the hotel_owner role"""
    updated_hotel = await HotelsService().update_hotel(
        transaction_manager=transaction_manager,
        hotel_id=hotel_id,
        name=new_hotel.name,
        location=new_hotel.location,
        services=new_hotel.services,
        rooms_quantity=new_hotel.rooms_quantity,
        owner_id=current_user.id,
    )
    logger.info(
        "Succesful created a new hotel", extra={"new_hotel_id": updated_hotel.id}
    )
    return updated_hotel


@router.patch(
    "/{hotel_id}/image",
    response_model=SHotelResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse},
    },
)
@version(1)
async def add_hotel_image(
    hotel_id: int,
    hotel_image: UploadFile,
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_hotel_owner),
):
    """Adds an image for the created hotel, current user must be a hotel owner"""
    updated_hotel = await HotelsService().add_hotel_image(
        transaction_manager=transaction_manager,
        hotel_id=hotel_id,
        hotel_image=hotel_image,
        owner_id=current_user.id,
    )
    logger.info(
        "Succesfully uploaded a hotel image",
        extra={"image_path": updated_hotel.image_path},
    )
    return updated_hotel


@router.delete(
    "/{hotel_id}/image",
    response_model=SHotelResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse},
    },
)
@version(1)
async def delete_hotel_image(
    hotel_id: int,
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_hotel_owner),
):
    """Deletes the image for a hotel by id, current user must be a hotel owner"""
    deleted_hotel = await HotelsService().delete_hotel_image(
        transaction_manager=transaction_manager,
        hotel_id=hotel_id,
        owner_id=current_user.id,
    )
    logger.info(
        "Succesfully deleted a hotel image",
        extra={"hotel_with_deleted_image_id": deleted_hotel.id},
    )
    return deleted_hotel


@router.delete(
    "/{hotel_id}",
    response_model=SHotelResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse},
    },
)
@version(1)
async def delete_hotel(
    hotel_id: int,
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_hotel_owner),
):
    """Deletes a hotel by id if the user is the owner of the hotel"""
    deleted_hotel = await HotelsService().delete_hotel(
        transaction_manager=transaction_manager,
        hotel_id=hotel_id,
        owner_id=current_user.id,
    )
    logger.info(
        "Succesfully deleted hotel", extra={"deleted_hotel_id": deleted_hotel.id}
    )
    return deleted_hotel


@router.get(
    "/{location}",
    response_model=Optional[list[SHotelsResponse]],
    responses={400: {"model": SExstraResponse}},
)
@cache(expire=60)
@version(1)
async def get_hotels_by_location_and_time(
    location: str,
    date_from: date,
    date_to: date,
    transaction_manager: TManagerDep,
):
    """Gives a list of hotels with free rooms for a certain date"""
    hotels = await HotelsService().get_hotels_by_location_and_time(
        transaction_manager=transaction_manager,
        location=location,
        date_from=date_from,
        date_to=date_to,
    )
    logger.info("Succesful return hotels")
    return hotels


@router.get(
    "/id/{hotel_id}",
    response_model=SHotelResponse,
    responses={404: {"model": SExstraResponse}},
)
@version(1)
@cache(expire=60)
async def get_hotel_by_id(hotel_id: int, transaction_manager: TManagerDep):
    """Returns the hotel by id"""
    hotel = await HotelsService().get_hotel_by_id(
        transaction_manager=transaction_manager, hotel_id=hotel_id
    )
    logger.info("Succesfully return a hotel", extra={"hotel_id": hotel.id})
    return hotel
