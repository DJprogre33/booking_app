from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi_versioning import version

from app.api.dependencies import get_rooms_service
from app.schemas.rooms import SRoomsResponse, SRooms
from app.services.rooms import RoomsService
from app.logger import logger


router = APIRouter(prefix="/hotels", tags=["Rooms"])


@router.get("/{hotel_id}/rooms", response_model=list[SRoomsResponse])
@version(1)
async def get_available_hotel_rooms(
    hotel_id: int,
    date_from: date,
    date_to: date,
    tasks_service: Annotated[RoomsService, Depends(get_rooms_service)],
):
    rooms = await tasks_service.get_availible_hotel_rooms(
        hotel_id=hotel_id, date_from=date_from, date_to=date_to
    )
    logger.info("Room list successfully received")
    return rooms


@router.post("/{hotel_id}/new")
@version(1)
async def create_room(
    hotel_id: int,
    new_room: SRooms,
    requets: Request,
    tasks_service: Annotated[RoomsService, Depends(get_rooms_service)]
):
    room_id = await tasks_service.create_room(
        hotel_id=hotel_id,
        name=new_room.name,
        description=new_room.description,
        price=new_room.price,
        services=new_room.services,
        quantity=new_room.quantity,
        request=requets
    )
    responce = {"room_id": room_id}

    logger.info("Room succesfully created", extra=responce)

    return responce


@router.delete("/{hotel_id}/{room_id}")
@version(1)
async def delete_room(
    hotel_id: int,
    room_id: int,
    request: Request,
    tasks_service: Annotated[RoomsService, Depends(get_rooms_service)]
):
    deleted_room_id = await tasks_service.delete_room(
        hotel_id=hotel_id,
        room_id=room_id,
        request=request
    )

    logger.info("Succesfully deleted room", extra={"deleted_room_id": room_id})

    return deleted_room_id

