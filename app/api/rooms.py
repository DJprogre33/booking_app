from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version

from app.dependencies import TManagerDep, get_current_hotel_owner
from app.exceptions import SExstraResponse
from app.logger import logger
from app.models.users import Users
from app.schemas.rooms import SRoomResponse, SRooms, SRoomsResponse
from app.services.rooms import RoomsService

router = APIRouter(prefix="/hotels", tags=["Rooms"])


@router.post(
    "/{hotel_id}/new",
    response_model=SRoomResponse,
    responses={
        400: {"model": SExstraResponse},
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse},
    },
)
@version(1)
async def create_room(
    hotel_id: int,
    room_data: SRooms,
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_hotel_owner),
):
    """Adds a room for a specific hotel, user must be the owner of the hotel"""
    new_room = await RoomsService().create_room(
        transaction_manager=transaction_manager,
        hotel_id=hotel_id,
        name=room_data.name,
        description=room_data.description,
        price=room_data.price,
        services=room_data.services,
        quantity=room_data.quantity,
        owner_id=current_user.id,
    )
    logger.info("Room succesfully created", extra={"room_id": new_room.id})
    return new_room


@router.put(
    "/{hotel_id}/{room_id}",
    response_model=SRoomResponse,
    responses={
        400: {"model": SExstraResponse},
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse},
    },
)
@version(1)
async def update_room(
    hotel_id: int,
    room_id: int,
    room_data: SRooms,
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_hotel_owner),
):
    """Adds a room for a specific hotel, user must be the owner of the hotel"""
    updated_room = await RoomsService().update_room(
        transaction_manager=transaction_manager,
        hotel_id=hotel_id,
        room_id=room_id,
        name=room_data.name,
        description=room_data.description,
        price=room_data.price,
        services=room_data.services,
        quantity=room_data.quantity,
        owner_id=current_user.id,
    )
    logger.info("Room succesfully created", extra={"room_id": updated_room.id})
    return updated_room


@router.delete(
    "/{hotel_id}/{room_id}",
    response_model=SRoomResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse},
    },
)
@version(1)
async def delete_room(
    hotel_id: int,
    room_id: int,
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_hotel_owner),
):
    """Deletes a room for a specific hotel, user must be the owner of the hotel"""
    deleted_room = await RoomsService().delete_room(
        transaction_manager=transaction_manager,
        hotel_id=hotel_id,
        room_id=room_id,
        owner_id=current_user.id,
    )
    logger.info("Succesfully deleted room", extra={"deleted_room_id": deleted_room.id})
    return deleted_room


@router.patch(
    "/{hotel_id}/{room_id}/image",
    response_model=SRoomResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse},
    },
)
async def add_room_image(
    hotel_id: int,
    room_id: int,
    room_image: UploadFile,
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_hotel_owner),
):
    """Adds an image for a specific room, user must be a hotel owner"""
    updated_room = await RoomsService().add_room_image(
        transaction_manager=transaction_manager,
        hotel_id=hotel_id,
        room_id=room_id,
        room_image=room_image,
        owner_id=current_user.id,
    )
    logger.info(
        "Succesfully uploaded a room image",
        extra={"image_path": updated_room.image_path},
    )
    return updated_room


@router.delete(
    "/{hotel_id}/{room_id}/image",
    response_model=SRoomResponse,
    responses={
        401: {"model": SExstraResponse},
        403: {"model": SExstraResponse},
        404: {"model": SExstraResponse},
    },
)
async def delete_room_image(
    hotel_id: int,
    room_id: int,
    transaction_manager: TManagerDep,
    current_user: Users = Depends(get_current_hotel_owner),
):
    """Deletes an image for a specific room, user must be a hotel owner"""
    updated_room = await RoomsService().delete_room_image(
        transaction_manager=transaction_manager,
        hotel_id=hotel_id,
        room_id=room_id,
        owner_id=current_user.id,
    )
    logger.info("Succesfully deleted a room image", extra={"room id": updated_room.id})
    return updated_room


@router.get(
    "/{hotel_id}/rooms",
    response_model=Optional[list[SRoomsResponse]],
    responses={400: {"model": SExstraResponse}, 404: {"model": SExstraResponse}},
)
@version(1)
async def get_available_hotel_rooms(
    hotel_id: int, date_from: date, date_to: date, transaction_manager: TManagerDep
):
    """Gives a list of available rooms for the selected hotel, for a certain date"""
    rooms = await RoomsService().get_availible_hotel_rooms(
        transaction_manager=transaction_manager,
        hotel_id=hotel_id,
        date_from=date_from,
        date_to=date_to,
    )
    logger.info("Rooms list successfully received", extra={"total_rooms": len(rooms)})
    return rooms


@router.get(
    "/rooms/{room_id}",
    response_model=SRoomResponse,
    responses={404: {"model": SExstraResponse}},
)
@version(1)
async def get_room(room_id: int, transaction_manager: TManagerDep):
    """Returns a specific room by id"""
    room = await RoomsService().get_room(
        transaction_manager=transaction_manager, room_id=room_id
    )
    logger.info("Room successfully received", extra={"room_id": room.id})
    return room
