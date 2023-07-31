import pytest
from httpx import AsyncClient

from app.repositories.users import UsersRepository

tasks_repo = UsersRepository


@pytest.mark.parametrize(
    "email,password,role,status_code",
    [
        ("user3@example.com", "user3", "", 422),
        ("user3@example.com", "user3", "admin", 422),
        ("user3example.com", "user3", "user", 422),
        ("user2@example.com", "user2", "user", 409),
        ("user3@example.com", "user3", "user", 200),
        ("owner3@example.com", "owner3", "hotel owner", 200),
    ],
)
async def test_register_user(
    email: str, password: str, role: str, status_code: int, async_client: AsyncClient
) -> None:
    response = await async_client.post(
        "/v1/auth/register", json={"email": email, "password": password, "role": role}
    )
    # Check status code
    assert response.status_code == status_code

    # Check detail for custom error
    if status_code == 409:
        assert response.json()["detail"] == "The user alredy exists"

    elif status_code == 200:
        # Check that user was created
        user = await tasks_repo.find_one_or_none(email=email)
        assert user.email == email
        assert user.role == role


@pytest.mark.parametrize(
    "email,password,status_code",
    [
        ("user3example.com", "user3", 422),
        ("user4@example.com", "user3", 401),
        ("user3@example.com", "wrong password", 401),
        ("user3@example.com", "user3", 200),
        ("owner3@example.com", "owner3", 200),
    ],
)
async def test_login_user(
    email: str, password: str, status_code: int, async_client: AsyncClient
) -> None:
    response = await async_client.post(
        "/v1/auth/login", json={"email": email, "password": password}
    )

    assert response.status_code == status_code

    # check 401 error
    if response.status_code == 401:
        assert response.json()["detail"] == "Invalid email or password"

    # check cookie header
    elif response.status_code == 200:
        assert "booking_access_token" in response.cookies


@pytest.mark.parametrize(
    "async_client_from_params,status_code,email",
    [
        ({"email": "user3@example.com", "password": "user3"}, 200, "user3@example.com"),
        ({"email": "user3@example.com", "password": "user2"}, 401, "user3@example.com"),
    ],
    indirect=["async_client_from_params"],
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
