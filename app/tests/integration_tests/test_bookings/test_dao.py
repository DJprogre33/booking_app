from datetime import datetime

import pytest

from app.repositories.bookings import BookingsRepository


@pytest.mark.parametrize(
    "user_id,room_id,date_from,date_to",
    [
        (2, 2, "2023-07-10", "2023-07-24")
    ]
)
async def test_add_read_delete_check_booking(
        user_id: int,
        room_id: int,
        date_from: str,
        date_to: str
):
    new_booking = await BookingDAO.add_booking(
        user_id=user_id,
        room_id=room_id,
        date_from=datetime.strptime(date_from, "%Y-%m-%d"),
        date_to=datetime.strptime(date_to, "%Y-%m-%d")
    )

    assert new_booking.user_id == user_id
    assert new_booking.room_id == room_id

    booking = await BookingDAO.find_one_or_none(id=new_booking.id)
    assert booking

    deleted_booking_id = await BookingDAO.delete_booking_by_id(user_id=user_id, booking_id=booking.id)
    assert deleted_booking_id == booking.id

    deleted_booking = await BookingDAO.find_one_or_none(id=new_booking.id)
    assert deleted_booking is None
