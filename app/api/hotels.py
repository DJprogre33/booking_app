from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi_cache.decorator import cache
from fastapi_versioning import version

from app.api.dependencies import get_hotels_service
from app.logger import logger
from app.schemas.hotels import SHotel, SHotelResponse, SHotelsResponse
from app.services.hotels import HotelsService


router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("/{location}", response_model=list[SHotelsResponse])
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

    logger.info("Succesful return hotels", extra={"total_hotels": len(hotels)})

    return


@router.get("/id/{hotel_id}", response_model=SHotelResponse)
@version(1)
async def get_hotel_by_id(
    hotel_id: int, tasks_service: Annotated[HotelsService, Depends(get_hotels_service)]
):
    """Returns the hotel by id"""
    hotel = await tasks_service.get_hotel_by_id(hotel_id=hotel_id)

    logger.info(
        "Succesfully return a hotel", extra={"hotel_id": hotel.id}
    )
    return hotel


@router.post("/new", response_model=SHotelResponse)
@version(1)
async def create_hotel(
    new_hotel: SHotel,
    request: Request,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
):
    """Creates a hotel if the user has the hotel_owner role"""
    new_hotel = await tasks_service.create_hotel(new_hotel=new_hotel, request=request)

    logger.info("Succesful created a new hotel", extra={"new_hotel_id": new_hotel.id})

    return new_hotel


@router.patch("/{hotel_id}/image", response_model=SHotelResponse)
@version(1)
async def add_hotel_image(
    hotel_id: int,
    hotel_image: UploadFile,
    request: Request,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
):
    """Adds an image for the created hotel"""
    result = await tasks_service.add_hotel_image(
        hotel_id=hotel_id, hotel_image=hotel_image, request=request
    )

    logger.info(
        "Succesfully uploaded a hotel image", extra={"image_path": result.image_path}
    )
    return result


@router.delete("/{hotel_id}/image")
@version(1)
async def delete_hotel_image(
    hotel_id: int,
    request: Request,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
) -> dict[str, int]:
    """Deletes the image for a hotel by id"""
    hotel_with_deleted_image = await tasks_service.delete_hotel_image(
        hotel_id=hotel_id, request=request
    )
    logger.info(
        "Succesfully deleted a hotel image",
        extra={"hotel_with_deleted_image_id": hotel_with_deleted_image.id},
    )
    return {"hotel with deleted image": hotel_with_deleted_image.id}


@router.delete("/{hotel_id}")
@version(1)
async def delete_hotel(
    hotel_id: int,
    request: Request,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
) -> dict[str, int]:
    """Deletes a hotel by id if the user is the owner of the hotel"""
    deleted_hotel_id = await tasks_service.delete_hotel(
        hotel_id=hotel_id, request=request
    )

    logger.info(
        "Succesfully deleted hotel", extra={"deleted_hotel_id": deleted_hotel_id}
    )
    return {"deleted_hotel_id": deleted_hotel_id}
