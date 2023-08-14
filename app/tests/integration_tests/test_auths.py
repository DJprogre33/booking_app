import pytest
from httpx import AsyncClient

from app.utils.transaction_manager import ITransactionManager


@pytest.mark.parametrize(
    "email,password,role,status_code",
    [
        ("user3@example.com", "user3", "", 422),
        ("user3@example.com", "user3", "admin", 422),
        ("user3example.com", "user3", "user", 422),
        ("user2@example.com", "user2", "user", 409),
        ("user3@example.com", "user3", "user", 201),
        ("owner3@example.com", "owner3", "hotel owner", 201),
    ],
)
async def test_register_user(
    email: str,
    password: str,
    role: str,
    status_code: int,
    async_client: AsyncClient,
    transaction_manager: ITransactionManager
) -> None:
    response = await async_client.post(
        "/v1/auth/register", json={"email": email, "password": password, "role": role}
    )
    # Check status code
    assert response.status_code == status_code

    # Check detail for custom error
    if status_code == 409:
        assert response.json()["detail"] == "The user alredy exists"

    elif status_code == 201:
        # Check that user was created
        async with transaction_manager:
            user = await transaction_manager.users.find_one_or_none(email=email)
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
        "/v1/auth/login", data={"username": email, "password": password}
    )
    assert response.status_code == status_code

    # check 401 error
    if response.status_code == 401:
        assert response.json()["detail"] == "Invalid email or password"

    # check cookies
    elif response.status_code == 200:
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        # logging out
        await async_client.post("/v1/auth/logout")


@pytest.mark.parametrize(
    "async_client_from_params,status_code",
    [
        ({"email": "user3@example.com", "password": "user3"}, 200)
    ],
    indirect=["async_client_from_params"]
)
async def test_logout_user(
    status_code: int,
    async_client_from_params: AsyncClient
) -> None:
    response = await async_client_from_params.post("/v1/auth/logout")
    assert response.status_code == status_code
    # check that cookies were deleted
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies

@pytest.mark.parametrize(
    "async_client_from_params,status_code",
    [
        ({"email": "user3@example.com", "password": "user3"}, 401),
        ({"email": "user3@example.com", "password": "user3"}, 200)

    ],
    indirect=["async_client_from_params"]
)
async def test_refresh_token(
    status_code: int,
    async_client_from_params: AsyncClient
) -> None:
    if status_code == 401:
        async_client_from_params.cookies.pop("refresh_token")

    response = await async_client_from_params.post("/v1/auth/refresh")
    assert response.status_code == status_code
    # abort all sessions
    await async_client_from_params.post("/v1/auth/abort")


@pytest.mark.parametrize(
    "email,password,total_sessions,status_code,user_id",
    [
        ("user3@example.com", "user3", 5, 200, 6)
    ],
)
async def test_abort_all_sessions(
    email: str,
    password: str,
    total_sessions: int,
    status_code: int,
    user_id: int,
    async_client: AsyncClient,
    transaction_manager: ITransactionManager
) -> None:
    for _ in range(total_sessions):
        await async_client.post(
            "/v1/auth/login", data={"username": email, "password": password}
        )
    # check total sessions
    async with transaction_manager:
        sessions = await transaction_manager.auth.find_all(user_id=user_id)
        assert len(sessions) == total_sessions
        # abort all sessions
        responce = await async_client.post("/v1/auth/abort")
        # check that all sessions were aborted
        sessions = await transaction_manager.auth.find_all(user_id=user_id)
        assert len(sessions) == 0
        assert responce.status_code == status_code
