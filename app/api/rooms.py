from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi_versioning import version

from app.api.dependencies import get_rooms_service
from app.logger import logger
from app.schemas.rooms import SRoomResponse, SRooms, SRoomsResponse
from app.services.rooms import RoomsService


router = APIRouter(prefix="/hotels", tags=["Rooms"])


@router.get("/{hotel_id}/rooms", response_model=Optional[list[SRoomsResponse]])
@version(1)
async def get_available_hotel_rooms(
    hotel_id: int,
    date_from: date,
    date_to: date,
    tasks_service: Annotated[RoomsService, Depends(get_rooms_service)],
):
    """Gives a list of available rooms for the selected hotel, for a certain date"""
    rooms = await tasks_service.get_availible_hotel_rooms(
        hotel_id=hotel_id, date_from=date_from, date_to=date_to
    )
    logger.info("Room list successfully received")
    return rooms


@router.post("/{hotel_id}/new", response_model=SRoomResponse)
@version(1)
async def create_room(
    hotel_id: int,
    new_room: SRooms,
    requets: Request,
    tasks_service: Annotated[RoomsService, Depends(get_rooms_service)],
):
    """Adds a room for a specific hotel, user must be the owner of the hotel"""
    new_room = await tasks_service.create_room(
        hotel_id=hotel_id,
        name=new_room.name,
        description=new_room.description,
        price=new_room.price,
        services=new_room.services,
        quantity=new_room.quantity,
        request=requets,
    )

    logger.info("Room succesfully created", extra={"room_id": new_room.id})

    return new_room


@router.delete("/{hotel_id}/{room_id}")
@version(1)
async def delete_room(
    hotel_id: int,
    room_id: int,
    request: Request,
    tasks_service: Annotated[RoomsService, Depends(get_rooms_service)],
) -> dict[str, int]:
    """Deletes a room for a specific hotel, user must be the owner of the hotel"""
    deleted_room_id = await tasks_service.delete_room(
        hotel_id=hotel_id, room_id=room_id, request=request
    )

    logger.info("Succesfully deleted room", extra={"deleted_room_id": room_id})

    return {"deleted room id": deleted_room_id}


@router.patch("/{hotel_id}/{room_id}/image", response_model=SRoomResponse)
async def add_room_image(
    hotel_id: int,
    room_id: int,
    room_image: UploadFile,
    request: Request,
    tasks_service: Annotated[RoomsService, Depends(get_rooms_service)],
):
    """Adds an image for a specific room, user must be a hotel owner"""
    result = await tasks_service.add_room_image(
        hotel_id=hotel_id, room_id=room_id, room_image=room_image, request=request
    )

    logger.info(
        "Succesfully uploaded a room image", extra={"image_path": result.image_path}
    )

    return result


@router.delete("/{hotel_id}/{room_id}/image")
async def delete_room_image(
    hotel_id: int,
    room_id: int,
    request: Request,
    tasks_service: Annotated[RoomsService, Depends(get_rooms_service)],
) -> dict[str, int]:
    """Deletes an image for a specific room, user must be a hotel owner"""
    room_with_deleted_image = await tasks_service.delete_room_image(
        hotel_id=hotel_id, room_id=room_id, request=request
    )

    logger.info(
        "Succesfully deleted a room image",
        extra={"room id": room_with_deleted_image.id},
    )

    return {"room with deleted image id": room_with_deleted_image.id}
