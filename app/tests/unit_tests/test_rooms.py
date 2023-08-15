from datetime import date

import pytest

from app.utils.transaction_manager import ITransactionManager


@pytest.mark.parametrize(
    "hotel_id,date_from,date_to,available_rooms,exists",
    [
        (1, date(2023, 10, 15), date(2023, 10, 15), 2, True),
        (7, date(2024, 12, 5), date(2024, 12, 25), 0, False),
        (8, date(2024, 12, 5), date(2024, 12, 25), 0, True),
    ],
)
async def test_get_available_hotel_rooms(
    hotel_id: int,
    date_from: date,
    date_to: date,
    available_rooms: int,
    exists: bool,
    transaction_manager: ITransactionManager,
) -> None:
    async with transaction_manager:
        rooms = await transaction_manager.rooms.get_available_hotel_rooms(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
        if exists:
            assert len(rooms) == available_rooms
            for room in rooms:
                assert room["hotel_id"] == hotel_id
                assert room["rooms_left"]
        else:
            assert not rooms


@pytest.mark.parametrize(
    "hotel_id,rooms_left,exists",
    [(1, 0, True), (3, 0, True), (7, 0, True), (8, 2, True), (9, 0, False)],
)
async def test_get_rooms_left(
    hotel_id: int,
    rooms_left: int,
    exists: bool,
    transaction_manager: ITransactionManager,
) -> None:
    async with transaction_manager:
        current_rooms_left = await transaction_manager.rooms.get_rooms_left(hotel_id)
        if exists:
            assert isinstance(current_rooms_left, int)
            assert current_rooms_left == rooms_left
        else:
            assert not current_rooms_left
