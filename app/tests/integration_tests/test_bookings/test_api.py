from httpx import AsyncClient
import pytest


@pytest.mark.parametrize(
    "room_id,date_from,date_to,booked_rooms,status_code",
    [
        *[(4, "2030-05-01", "2030-05-15", i, 200) for i in range(3, 11)] +
        [(4, "2030-05-01", "2030-05-15", 10, 409)] * 2
    ]
)
async def test_add_and_get_booking(
        room_id: int,
        date_from: str,
        date_to: str,
        booked_rooms: int,
        status_code: int,
        auth_async_client: AsyncClient
):
    responce = await auth_async_client.post(
        "/bookings",
        params={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )

    assert responce.status_code == status_code

    total_hotels = await auth_async_client.get("/bookings")

    assert len(total_hotels.json()) == booked_rooms
