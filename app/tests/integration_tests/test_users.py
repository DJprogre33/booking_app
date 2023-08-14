import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "async_client_from_params,status_code,email",
    [
        ({"email": "user3@example.com", "password": "user3"}, 200, "user3@example.com"),
        ({"email": "user3@example.com", "password": "user2"}, 401, "user3@example.com"),
        ({"email": "user3example.com", "password": "user2"}, 422, "user3@example.com")
    ],
    indirect=["async_client_from_params"]
)
async def test_get_me(
    async_client_from_params: AsyncClient, status_code: int, email: str
) -> None:
    response = await async_client_from_params.get("/v1/auth/me")
    assert response.status_code == status_code

    if response.status_code == 200:
        assert response.json()["email"] == email


@pytest.mark.parametrize(
    "async_client_from_params,status_code",
    [
        ({"email": "user3@example.com", "password": "user2"}, 401),
        ({"email": "user3@example.com", "password": "user3"}, 200),
        ({"email": "user3@example.com", "password": "user3"}, 401),
        ({"email": "owner3@example.com", "password": "owner2"}, 401),
        ({"email": "owner3@example.com", "password": "owner3"}, 200),
    ],
    indirect=["async_client_from_params"],
)
async def test_delete_me(
    async_client_from_params: AsyncClient, status_code: int
) -> None:
    response = await async_client_from_params.delete("/v1/auth/me")
    assert response.status_code == status_code
    if status_code == 200:
        deleted_user = await tasks_repo.find_one_or_none(
            email="user3@example.com"
        )
        assert not deleted_user
