import pytest
from httpx import AsyncClient
from app.repositories.users import UsersRepository


tasks_repo = UsersRepository()

# Fixture for getting status code in parametrize fixture tests
@pytest.fixture(scope="function")
def status_code(request):
    # Получение значения статусного кода из параметров тестовой функции
    return request.param


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
    responce = await async_client.post(
        "/auth/register", json={"email": email, "password": password, "role": role}
    )
    # Check status code
    assert responce.status_code == status_code

    # Check detail for custom error
    if status_code == 409:
        assert responce.json()["detail"] == "The user alredy exists"

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
    responce = await async_client.post(
        "/auth/login", json={"email": email, "password": password}
    )

    assert responce.status_code == status_code

    # check 401 error
    if responce.status_code == 401:
        assert responce.json()["detail"] == "Invalid email or password"

    # check cookie header
    elif responce.status_code == 200:
        assert "booking_access_token" in responce.cookies

@pytest.mark.parametrize(
    "async_client_from_params,status_code",
    [
        ({"email": "user3@example.com", "password": "user3"}, 200),
        ({"email": "user3@example.com", "password": "user2"}, 401)
    ],
    indirect=True
)
async def test_get_me(
    async_client_from_params: AsyncClient,
    status_code: int
) -> None:
    # try to get with auth user

    response = await async_client_from_params.get("/auth/me")
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "async_client_from_params,status_code",
    [
        ({"email": "user3@example.com", "password": "user2"}, 401),
        ({"email": "user3@example.com", "password": "user3"}, 200),
        ({"email": "user3@example.com", "password": "user3"}, 401)
    ],
    indirect=True
)
async def test_delete_me(
    async_client_from_params: AsyncClient,
    status_code: int
) -> None:
    response = await async_client_from_params.delete("/auth/me")
    assert response.status_code == status_code