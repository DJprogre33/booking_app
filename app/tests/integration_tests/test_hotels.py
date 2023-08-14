from typing import Union

import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "location,date_from,date_to,status_code,total_hotels",
    [
        ("Алтай", "2023-09-15", "2023-09-12", 400, None),
        ("Алтай", "2023-09-15", "2023-09-15", 400, None),
        ("Алтай", "2022-09-15", "2023-09-20", 400, None),
        ("Алтай", "2022-09-15", "2023-09-20", 400, None),
        ("Москва", "2024-09-15", "2024-09-20", 200, 0),
        ("Ижора", "2024-12-05", "2024-12-25", 200, 0),
        ("Ижора", "2024-12-01", "2024-12-05", 200, 0),
        ("Ижора", "2024-12-06", "2024-12-10", 200, 0),
        ("Ижора", "2024-12-25", "2024-12-30", 200, 0),
        ("Ижора", "2024-11-01", "2024-11-05", 200, 1),
        ("Алтай", "2024-11-01", "2024-11-05", 200, 3),
        ("Коми", "2024-11-01", "2024-11-05", 200, 2),
        ("Будапешт", "2024-01-01", "2024-01-02", 200, 0)
    ],
)
async def test_get_hotels_by_location_and_time(
    location: str,
    date_from: str,
    date_to: str,
    status_code: int,
    total_hotels: Union[int, None],
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(
        f"/v1/hotels/{location}", params={"date_from": date_from, "date_to": date_to}
    )

    assert response.status_code == status_code

    if response.status_code == 400:
        error_detail = (
            "Incorrect data range, data range must be"
            "1 <= data_to - data_from <= 90"
            "and date_from can't be earlier then now"
        )

        assert response.json()["detail"] == error_detail
    else:
        response_json = response.json()
        if response_json:
            assert len(response_json) == total_hotels
        else:
            assert bool(response_json) == total_hotels


@pytest.mark.parametrize(
    "hotel_id,status_code", [(1, 200), (3, 200), (7, 200), (-1, 404), (9, 404)]
)
async def test_get_hotel_by_id(
    hotel_id: int, status_code: int, async_client: AsyncClient
):
    response = await async_client.get(f"/v1/hotels/id/{hotel_id}")
    assert response.status_code == status_code

    if status_code == 404:
        assert response.json()["detail"] == "The hotel not found by id"
    else:
        assert response.json()["id"] == hotel_id


@pytest.mark.parametrize(
    "async_client_from_params,name,location,services,rooms_quantity,status_code",
    [
        (
            {"email": "user2@example.com", "password": "user1"},
            "Паучок",
            "г.Сочи ул.Позднякова",
            ["Wi-FI"],
            5,
            401,
        ),
        (
            {"email": "user2@example.com", "password": "user2"},
            "Паучок",
            "г.Сочи ул.Позднякова",
            ["Wi-FI"],
            5,
            403,
        ),
        (
            {"email": "owner1@example.com", "password": "owner1"},
            "Паучок",
            "г.Сочи ул.Позднякова",
            ["Wi-FI"],
            0,
            422,
        ),
        (
            {"email": "owner1@example.com", "password": "owner1"},
            "Паучок",
            "г.Сочи ул.Позднякова",
            ["Wi-FI"],
            5,
            200,
        ),
    ],
    indirect=["async_client_from_params"],
)
async def test_create_hotel(
    async_client_from_params: AsyncClient,
    name: str,
    location: str,
    services: list,
    rooms_quantity: int,
    status_code: int,
) -> None:
    response = await async_client_from_params.post(
        "/v1/hotels/new",
        json={
            "name": name,
            "location": location,
            "services": services,
            "rooms_quantity": rooms_quantity,
        },
    )
    assert response.status_code == status_code

    # check that we created correct hotel, which returns by .returning() method
    if status_code == 200:
        response_json = response.json()
        assert response_json["name"] == name
        assert response_json["location"] == location
        assert response_json["services"] == services
        assert response_json["rooms_quantity"] == rooms_quantity


@pytest.mark.parametrize(
    "async_client_from_params,name,location,services,rooms_quantity,status_code,hotel_id",
    [
        (
            {"email": "user2@example.com", "password": "user1"},
            "Паучок",
            "г.Сочи ул.Позднякова",
            ["Wi-FI"],
            5,
            401,
            None
        ),
        (
            {"email": "user2@example.com", "password": "user2"},
            "Паучок",
            "г.Сочи ул.Позднякова",
            ["Wi-FI"],
            5,
            403,
            None
        ),
        (
            {"email": "owner1@example.com", "password": "owner1"},
            "Паучок",
            "г.Сочи ул.Позднякова",
            ["Wi-FI"],
            0,
            422,
            None
        ),
        (
            {"email": "owner1@example.com", "password": "owner1"},
            "Паучок",
            "г.Сочи ул.Позднякова",
            ["Wi-FI"],
            5,
            404,
            10
        ),
        (
            {"email": "owner1@example.com", "password": "owner1"},
            "Паучок",
            "г.Сочи ул.Позднякова",
            ["Wi-FI"],
            5,
            200,
            9
        ),
    ],
    indirect=["async_client_from_params"],
)
async def test_update_hotel(
    async_client_from_params: AsyncClient,
    name: str,
    location: str,
    services: list,
    rooms_quantity: int,
    status_code: int,
    hotel_id: int
) -> None:
    response = await async_client_from_params.put(
        f"/v1/hotels/{hotel_id}",
        json={
            "name": name,
            "location": location,
            "services": services,
            "rooms_quantity": rooms_quantity,
        },
    )
    assert response.status_code == status_code

    # check that we updated correct hotel
    if status_code == 200:
        response_json = response.json()
        assert response_json["name"] == name
        assert response_json["location"] == location
        assert response_json["services"] == services
        assert response_json["rooms_quantity"] == rooms_quantity


@pytest.mark.parametrize(
    "async_client_from_params,hotel_id,status_code",
    [
        ({"email": "user1@example.com", "password": "owner1"}, 1, 401),
        ({"email": "owner2@example.com", "password": "owner2"}, 1, 403),
        ({"email": "user1@example.com", "password": "user1"}, 1, 403),
        ({"email": "owner1@example.com", "password": "owner1"}, 10, 404),
        ({"email": "owner1@example.com", "password": "owner1"}, 1, 200),
    ],
    indirect=["async_client_from_params"],
)
async def test_add_hotel_image(
    async_client_from_params: AsyncClient, hotel_id: int, status_code: int
):
    filepath = "app/tests/integration_tests/test_image.png"
    with open(filepath, "rb") as image_file:
        files = {"hotel_image": (filepath, image_file)}
        response = await async_client_from_params.patch(
            f"/v1/hotels/{hotel_id}/image", files=files
        )
    assert response.status_code == status_code

    if response.status_code == 200:
        assert response.json()["image_path"]


@pytest.mark.parametrize(
    "async_client_from_params,hotel_id,status_code",
    [
        ({"email": "user1@example.com", "password": "owner1"}, 1, 401),
        ({"email": "owner2@example.com", "password": "owner2"}, 1, 403),
        ({"email": "user1@example.com", "password": "user1"}, 1, 403),
        ({"email": "owner1@example.com", "password": "owner1"}, 10, 404),
        ({"email": "owner1@example.com", "password": "owner1"}, 1, 200),
    ],
    indirect=["async_client_from_params"],
)
async def test_delete_hotel_image(
    async_client_from_params: AsyncClient, hotel_id: int, status_code: int
):
    response = await async_client_from_params.delete(f"/v1/hotels/{hotel_id}/image")
    assert response.status_code == status_code

    if response.status_code == 200:
        assert not response.json().get("image_path")


@pytest.mark.parametrize(
    "async_client_from_params,hotel_id,status_code",
    [
        ({"email": "user1@example.com", "password": "owner1"}, 1, 401),
        ({"email": "owner2@example.com", "password": "owner2"}, 1, 403),
        ({"email": "user1@example.com", "password": "user1"}, 1, 403),
        ({"email": "owner1@example.com", "password": "owner1"}, 10, 404),
        ({"email": "owner1@example.com", "password": "owner1"}, 9, 200),
    ],
    indirect=["async_client_from_params"],
)
async def test_delete_hotel(
    async_client_from_params: AsyncClient, hotel_id: int, status_code: int
):
    response = await async_client_from_params.delete(f"/v1/hotels/{hotel_id}")
    assert response.status_code == status_code

    if response.status_code == 200:
        assert response.json()["id"] == hotel_id
