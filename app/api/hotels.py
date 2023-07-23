from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Request
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
    return await tasks_service.get_hotels_by_location_and_time(
        location=location, date_from=date_from, date_to=date_to
    )


@router.get("/id/{hotel_id}", response_model=SHotelResponse)
@version(1)
async def get_hotel_by_id(
    hotel_id: int, tasks_service: Annotated[HotelsService, Depends(get_hotels_service)]
):
    return await tasks_service.get_hotel_by_id(hotel_id=hotel_id)


@router.post("/new")
@version(1)
async def create_hotel(
    new_hotel: SHotel,
    request: Request,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
):
    new_hotel_id = await tasks_service.create_hotel(new_hotel=new_hotel, request=request)

    logger.info("Succesful created a new hotel", extra={"new_hotel_id": new_hotel_id})

    return {"new_hotel_id": new_hotel_id}


@router.patch("/{hotel_id}/image", response_model=SHotelResponse)
@version(1)
async def add_hotel_image(
    hotel_id: int,
    hotel_image: UploadFile,
    request: Request,
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)],
):
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
    tasks_service: Annotated[HotelsService, Depends(get_hotels_service)]
):
    hotel_id = await tasks_service.delete_hotel_image(hotel_id=hotel_id, request=request)
    logger.info("Succesfully deleted a hotel image", extra={"hotel_id": hotel_id})

    return {"ID of the hotel where the image was deleted": hotel_id}


@router.patch("/{hotel_id}")
@version(1)
async def edit_hotel_data():
    pass


@router.delete("/{hotel_id}")
@version(1)
async def delete_hotel():
    pass