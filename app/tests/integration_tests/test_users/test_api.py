import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "email,password,status_code",
    [
        ("test@gmail.com", "test", 200),
        ("test@gmail.com", "test", 409),
        ("bad_email", "password", 422)
    ]
)
async def test_register_user(email: str, password: str, status_code: int, async_client: AsyncClient):
    responce = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password
        }
    )

    assert responce.status_code == status_code


@pytest.mark.parametrize(
    "email,password,status_code",
    [
        ("test@test.com", "test", 200),
        ("artem@example.com", "artem", 200),
        ("unregistereduser@mail.com", "password", 401),
        ("bademail", "password", 422)
    ]
)
async def test_login_user(email: str, password: str, status_code: int, async_client: AsyncClient):
    responce = await async_client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert responce.status_code == status_code