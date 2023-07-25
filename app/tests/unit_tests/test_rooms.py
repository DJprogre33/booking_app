import pytest
from datetime import date
from app.repositories.rooms import RoomsRepository
from app.exceptions import IncorrectHotelIDException

tasks_repo = RoomsRepository()

@pytest.mark.parametrize(
    "hotel_id,date_from,date_to,available_rooms",
    [
        (1, date(2023, 10, 15), date(2023, 10, 15), 2),
        (7, date(2024, 12, 5), date(2024, 12, 25), 0),
        (8, date(2024, 12, 5), date(2024, 12, 25), 0)
    ]
)
async def test_get_available_hotel_rooms(
    hotel_id: int,
    date_from: date,
    date_to: date,
    available_rooms: int
) -> None:
    if hotel_id == 8:
        with pytest.raises(IncorrectHotelIDException):
            await tasks_repo.get_available_hotel_rooms(
                hotel_id=hotel_id,
                date_from=date_from,
                date_to=date_to
            )
    else:
        rooms = await tasks_repo.get_available_hotel_rooms(
            hotel_id=hotel_id,
            date_from=date_from,
            date_to=date_to
        )
        assert len(rooms) == available_rooms

        for room in rooms:
            assert room["hotel_id"] == hotel_id
            assert room["rooms_left"]


@pytest.mark.parametrize(
    "hotel_id,rooms_left",
    [
        (1, 0),
        (3, 0),
        (7, 0),
        (8, 0)
    ]
)
async def test_get_rooms_left(hotel_id: int, rooms_left: int):
    if hotel_id == 8:
        with pytest.raises(IncorrectHotelIDException):
            await tasks_repo.get_rooms_left(hotel_id)
    else:
        current_rooms_left = await tasks_repo.get_rooms_left(hotel_id)

        assert isinstance(current_rooms_left, int)
        assert current_rooms_left == rooms_left
