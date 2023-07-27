import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "room_id,date_from,date_to,booked_rooms,status_code",
    [
        *[(4, "2030-05-01", "2030-05-15", i, 200) for i in range(4, 12)]
        + [(4, "2030-05-01", "2030-05-15", 11, 409)] * 2
        + [(4, "2030-05-01", "2030-05-01", 11, 400)]
    ],
)
async def test_add_and_get_booking(
    room_id: int,
    date_from: str,
    date_to: str,
    booked_rooms: int,
    status_code: int,
    auth_async_client: AsyncClient,
) -> None:
    """In this test function we order until we run out of numbers,
    then there's an error."""
    responce = await auth_async_client.post(
        "v1/bookings",
        params={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert responce.status_code == status_code

    total_hotels = await auth_async_client.get("/v1/bookings")
    assert len(total_hotels.json()) == booked_rooms


async def test_get_and_delete_all_bookings(auth_async_client: AsyncClient) -> None:
    """In this test function we get all users order
    and then delete them all."""
    responce = await auth_async_client.get("/v1/bookings")
    bookings_dict = responce.json()

    assert responce.status_code == 200
    assert len(bookings_dict) == 11

    for booking in bookings_dict:
        responce = await auth_async_client.delete(f"/v1/bookings/{booking['id']}")
        assert responce.status_code == 200
        assert responce.json()["deleted_booking_id"] == booking["id"]

    responce = await auth_async_client.get("/v1/bookings")

    assert responce.status_code == 200
    assert not responce.json()


@pytest.mark.parametrize(
    "async_client_from_params,room_id,date_from,date_to,status_code",
    [
        (
            {"email": "user1@example.com", "password": "user1"},
            12,
            "2024-12-05",
            "2024-12-25",
            200,
        ),
        (
            {"email": "user1@example.com", "password": "user1"},
            13,
            "2024-12-05",
            "2024-12-25",
            409,
        ),
    ],
    indirect=["async_client_from_params"],
)
async def test_add_booking(
    async_client_from_params: AsyncClient,
    room_id: int,
    date_from: str,
    date_to: str,
    status_code: int,
) -> None:
    responce = await async_client_from_params.post(
        "/v1/bookings",
        params={"room_id": room_id, "date_from": date_from, "date_to": date_to},
    )
    assert responce.status_code == status_code
