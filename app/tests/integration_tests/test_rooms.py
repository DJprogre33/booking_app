from typing import Union

import pytest
from httpx import AsyncClient

from app.repositories.rooms import RoomsRepository


tasks_repo = RoomsRepository


@pytest.mark.parametrize(
    "hotel_id,date_from,date_to,status_code,available_rooms",
    [
        (1, "2023-05-05", "2023-05-05", 400, None),
        (1, "2023-05-05", "2023-05-04", 400, None),
        (1, "2023-05-05", "2023-05-04", 400, None),
        (1, "2023-05-05", "2023-05-05", 400, None),
        (1, "2024-05-05", "2024-05-10", 200, 2),
        (3, "2024-05-05", "2024-05-10", 200, 2),
        (7, "2024-12-05", "2024-12-25", 200, 0),
        (7, "2024-12-01", "2024-12-06", 200, 0),
    ],
)
async def test_get_available_hotel_rooms(
    hotel_id: int,
    date_from: str,
    date_to: str,
    status_code: int,
    available_rooms: Union[int, None],
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(
        f"/v1/hotels/{hotel_id}/rooms", params={"date_from": date_from, "date_to": date_to}
    )
    assert response.status_code == status_code

    if response.status_code == 200:
        assert len(response.json()) == available_rooms


@pytest.mark.parametrize(
    "async_client_from_params,hotel_id,room_id,rooms_left,status_code",
    [
        ({"email": "user2@example.com", "password": "user1"}, 1, 1, None, 401),
        ({"email": "user2@example.com", "password": "user2"}, 1, 1, None, 403),
        ({"email": "owner1@example.com", "password": "owner1"}, 1, 15, None, 404),
        ({"email": "owner1@example.com", "password": "owner1"}, 1, 1, 5, 200),
        ({"email": "owner1@example.com", "password": "owner1"}, 1, 1, None, 404),
        ({"email": "owner2@example.com", "password": "owner2"}, 7, 13, 1, 200),
    ],
    indirect=["async_client_from_params"],
)
async def test_delete_room(
    async_client_from_params: AsyncClient,
    hotel_id: int,
    room_id: int,
    rooms_left: Union[int, None],
    status_code: int,
):
    response = await async_client_from_params.delete(f"/v1/hotels/{hotel_id}/{room_id}")
    assert response.status_code == status_code

    if status_code == 200:
        response.json()["deleted_room_id"] = room_id
        rooms = await tasks_repo.get_rooms_left(hotel_id)
        assert rooms == rooms_left


@pytest.mark.parametrize(
    "async_client_from_params,hotel_id,name,description,price,services,quantity,status_code",
    [
        (
            {"email": "user2@example.com", "password": "user1"},
            1,
            "Супер люкс",
            "Очень дорогой номер",
            30000,
            ["Wi-FI", "Джакузи", "Сауна"],
            5,
            401,
        ),
        (
            {"email": "user2@example.com", "password": "user2"},
            1,
            "Супер люкс",
            "Очень дорогой номер",
            30000,
            ["Wi-FI", "Джакузи", "Сауна"],
            5,
            403,
        ),
        (
            {"email": "owner1@example.com", "password": "owner1"},
            1,
            "Супер люкс",
            "Очень дорогой номер",
            30000,
            ["Wi-FI", "Джакузи", "Сауна"],
            6,
            400,
        ),
        (
            {"email": "owner1@example.com", "password": "owner1"},
            1,
            "Супер люкс",
            "Очень дорогой номер",
            30000,
            ["Wi-FI", "Джакузи", "Сауна"],
            5,
            200,
        ),
        (
            {"email": "owner2@example.com", "password": "owner2"},
            7,
            "Супер люкс",
            "Очень дорогой номер",
            30000,
            ["Wi-FI", "Джакузи", "Сауна"],
            2,
            400,
        ),
        (
            {"email": "owner2@example.com", "password": "owner2"},
            7,
            "Супер люкс",
            "Очень дорогой номер",
            30000,
            ["Wi-FI", "Джакузи", "Сауна"],
            1,
            200,
        ),
    ],
    indirect=["async_client_from_params"],
)
async def test_create_room(
    async_client_from_params: AsyncClient,
    hotel_id: int,
    name: str,
    description: str,
    price: int,
    services: list,
    quantity: int,
    status_code: int,
) -> None:
    response = await async_client_from_params.post(
        f"/v1/hotels/{hotel_id}/new",
        json={
            "hotel_id": hotel_id,
            "name": name,
            "description": description,
            "price": price,
            "services": services,
            "quantity": quantity,
        },
    )
    assert response.status_code == status_code

    # check that we created correct hotel, which returns by .returning() method
    if status_code == 200:
        response_json = response.json()
        assert response_json["name"] == name
        assert response_json["hotel_id"] == hotel_id
        assert response_json["price"] == price
        assert response_json["services"] == services
        assert response_json["quantity"] == quantity

        # Get created room from db
        room = await tasks_repo.find_one_or_none(id=response_json["id"])
        assert room.id == response_json["id"]
        assert room.name == name
        assert room.hotel_id == hotel_id
        assert room.price == price
        assert room.services == services
        assert room.quantity == quantity


@pytest.mark.parametrize(
    "async_client_from_params,hotel_id,room_id,status_code",
    [
        ({"email": "user1@example.com", "password": "owner1"}, 1, 2, 401),
        ({"email": "owner2@example.com", "password": "owner2"}, 1, 2, 403),
        ({"email": "user1@example.com", "password": "user1"}, 1, 2, 403),
        ({"email": "owner1@example.com", "password": "owner1"}, 1, 2, 200),
    ],
    indirect=["async_client_from_params"],
)
async def test_add_hotel_image(
    async_client_from_params: AsyncClient, hotel_id: int, room_id: int, status_code: int
):
    filepath = "app/tests/integration_tests/test_image.png"
    with open(filepath, "rb") as image_file:
        files = {"room_image": (filepath, image_file)}
        response = await async_client_from_params.patch(
            f"/v1/hotels/{hotel_id}/{room_id}/image", files=files
        )
    assert response.status_code == status_code

    if response.status_code == 200:
        room = await tasks_repo.find_one_or_none(id=response.json()["id"])
        assert room.image_path
        assert room.id == room_id


@pytest.mark.parametrize(
    "async_client_from_params,hotel_id,room_id,status_code",
    [
        ({"email": "user1@example.com", "password": "owner1"}, 1, 2, 401),
        ({"email": "owner2@example.com", "password": "owner2"}, 1, 2, 403),
        ({"email": "user1@example.com", "password": "user1"}, 1, 2, 403),
        ({"email": "owner1@example.com", "password": "owner1"}, 1, 2, 200),
    ],
    indirect=["async_client_from_params"],
)
async def test_add_hotel_image(
    async_client_from_params: AsyncClient, hotel_id: int, room_id: int, status_code: int
):
    response = await async_client_from_params.delete(
        f"/v1/hotels/{hotel_id}/{room_id}/image"
    )
    assert response.status_code == status_code

    if response.status_code == 200:
        room = await tasks_repo.find_one_or_none(
            id=response.json()["room with deleted image id"]
        )
        assert not room.image_path
        assert room.id == room_id
