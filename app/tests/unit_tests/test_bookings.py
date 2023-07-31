from datetime import date

import pytest

from app.exceptions import IncorrectBookingIdException, RoomCanNotBeBookedException
from app.models.bookings import Bookings
from app.repositories.bookings import BookingsRepository


tasks_repo = BookingsRepository


@pytest.mark.parametrize("user_id,total_bookings", [(1, 3), (2, 2)])
async def test_get_bookings(user_id: int, total_bookings: int) -> None:
    bookings = await tasks_repo.get_bookings(user_id)
    assert len(bookings) == total_bookings

    for booking in bookings:
        assert booking.user_id == user_id


@pytest.mark.parametrize(
    "user_id,room_id,date_from,date_to,fail",
    [
        (1, 1, date(2023, 9, 30), date(2023, 10, 30), False),
        (2, 3, date(2023, 9, 30), date(2023, 10, 30), False),
        (2, 12, date(2024, 12, 15), date(2024, 12, 25), True),
        (1, 13, date(2024, 12, 15), date(2024, 12, 25), True),
        (2, 12, date(2023, 12, 15), date(2023, 12, 25), False),
        (1, 13, date(2023, 12, 15), date(2023, 12, 25), False),
    ],
)
async def test_add_booking(
    user_id: int, room_id: int, date_from: date, date_to: date, fail: bool
) -> None:
    if fail:
        with pytest.raises(RoomCanNotBeBookedException):
            await tasks_repo.add_booking(
                user_id=user_id, room_id=room_id, date_from=date_from, date_to=date_to
            )
    else:
        booking = await tasks_repo.add_booking(
            user_id=user_id, room_id=room_id, date_from=date_from, date_to=date_to
        )
        assert isinstance(booking, Bookings)
        assert booking.room_id == room_id
        assert booking.date_from == date_from
        assert booking.date_to == date_to


@pytest.mark.parametrize(
    "user_id,booking_id,fail",
    [
        (2, 6, True),
        (2, 10, True),
        (1, 8, True),
        (10, 9, True),
        (1, 6, False),
        (2, 7, False),
        (2, 8, False),
        (1, 9, False),
    ],
)
async def test_delete_bookings(user_id: int, booking_id: int, fail: bool) -> None:
    if fail:
        with pytest.raises(IncorrectBookingIdException):
            await tasks_repo.delete_booking_by_id(
                user_id=user_id, booking_id=booking_id
            )
    else:
        deleted_booking_id = await tasks_repo.delete_booking_by_id(
            user_id=user_id, booking_id=booking_id
        )
        assert deleted_booking_id == booking_id
