from datetime import date

import pytest

from app.exceptions import IncorrectBookingIdException, RoomCanNotBeBookedException
from app.models.bookings import Bookings
from app.utils.transaction_manager import ITransactionManager


@pytest.mark.parametrize(
    "user_id,total_bookings,exists",
    [(1, 3, True), (2, 2, True), (3, 0, False)]
)
async def test_get_bookings(
    user_id: int,
    total_bookings: int,
    exists: bool,
    transaction_manager: ITransactionManager
) -> None:
    async with transaction_manager:
        bookings = await transaction_manager.bookings.get_bookings(user_id)
        if exists:
            assert len(bookings) == total_bookings
            for booking in bookings:
                assert booking.user_id == user_id
        else:
            assert not bookings


@pytest.mark.parametrize(
    "user_id,booking_id,exists",
    [
        (1, 1, True),
        (1, 2, True),
        (2, 3, True),
        (1, 4, True),
        (1, 6, False),
        (2, 1, False),
        (3, 1, False),
        (0, 0, False),
    ],
)
async def test_delete_bookings(
    user_id: int,
    booking_id: int,
    exists: bool,
    transaction_manager: ITransactionManager
) -> None:
    async with transaction_manager:
        deleted_booking = await transaction_manager.bookings.delete(
            id=booking_id, user_id=user_id
        )
        if exists:
            assert deleted_booking.id == booking_id
        else:
            assert not deleted_booking
        await transaction_manager.rollback()
