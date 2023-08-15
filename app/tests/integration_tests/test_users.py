import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "async_client_from_params,offset,limit,status_code,total_users",
    [
        ({"email": "user2@example.com", "password": "user2"}, None, None, 403, 7),
        ({"email": "owner2@example.com", "password": "owner2"}, None, None, 403, 7),
        ({"email": "admin@example.com", "password": "admin"}, 0, 10, 200, 5),
        ({"email": "admin@example.com", "password": "admin"}, 0, 4, 200, 4),
        ({"email": "admin@example.com", "password": "admin"}, 1, 3, 200, 3),
    ],
    indirect=["async_client_from_params"],
)
async def test_get_users_list(
    status_code: int,
    total_users: int,
    offset: int,
    limit: int,
    async_client_from_params: AsyncClient,
) -> None:
    responce = await async_client_from_params.get(
        "/v1/users", params={"offset": offset, "limit": limit}
    )
    assert responce.status_code == status_code
    if responce.status_code == 200:
        assert len(responce.json()) == total_users


@pytest.mark.parametrize(
    "async_client_from_params,status_code,email",
    [
        ({"email": "user2@example.com", "password": "user2"}, 200, "user2@example.com"),
        ({"email": "user2@example.com", "password": "user1"}, 401, "user3@example.com"),
        ({"email": "user3example.com", "password": "user2"}, 401, "user3@example.com"),
    ],
    indirect=["async_client_from_params"],
)
async def test_return_me(
    async_client_from_params: AsyncClient, status_code: int, email: str
) -> None:
    response = await async_client_from_params.get("/v1/users/me")
    assert response.status_code == status_code

    if response.status_code == 200:
        assert response.json()["email"] == email


@pytest.mark.parametrize(
    "async_client_from_params,status_code,new_email,new_password",
    [
        ({"email": "user2@example.com", "password": "user1"}, 401, None, None),
        ({"email": "user3example.com", "password": "user2"}, 401, None, None),
        (
            {"email": "user2@example.com", "password": "user2"},
            200,
            "new_user2@example.com",
            "new_user2",
        ),
    ],
    indirect=["async_client_from_params"],
)
async def test_update_me(
    async_client_from_params: AsyncClient,
    status_code: int,
    new_email: str,
    new_password: str,
) -> None:
    response = await async_client_from_params.put(
        "/v1/users/me", json={"email": new_email, "password": new_password}
    )
    assert response.status_code == status_code

    # check updated credentials
    if response.status_code == 200:
        response_json = response.json()
        assert response_json["email"] == new_email
        # undo changes
        await async_client_from_params.put(
            "/v1/users/me",
            json={
                "email": new_email.lstrip("new_"),
                "password": new_password.lstrip("new_"),
            },
        )


@pytest.mark.parametrize(
    "async_client_from_params,status_code,email,password,role",
    [
        ({"email": "user2@example.com", "password": "user1"}, 401, None, None, None),
        ({"email": "user3example.com", "password": "user2"}, 401, None, None, None),
        (
            {"email": "user2@example.com", "password": "user2"},
            200,
            "user2@example.com",
            "user2",
            "user",
        ),
    ],
    indirect=["async_client_from_params"],
)
async def test_delete_me(
    async_client_from_params: AsyncClient,
    status_code: int,
    email: str,
    password: str,
    role: str,
) -> None:
    response = await async_client_from_params.delete("/v1/users/me")
    assert response.status_code == status_code

    if response.status_code == 200:
        response_json = response.json()
        assert response_json["email"] == email
        assert response_json["role"] == role
        # undo changes
        await async_client_from_params.post(
            "/v1/auth/register",
            json={"email": email, "password": password, "role": role},
        )


@pytest.mark.parametrize(
    "async_client_from_params,status_code,user_id",
    [
        ({"email": "user2@example.com", "password": "user1"}, 401, None),
        ({"email": "user3example.com", "password": "user2"}, 401, None),
        ({"email": "user2@example.com", "password": "user2"}, 403, None),
        ({"email": "owner2@example.com", "password": "owner2"}, 403, None),
        ({"email": "admin@example.com", "password": "admin"}, 404, 10),
        ({"email": "admin@example.com", "password": "admin"}, 200, 6),
    ],
    indirect=["async_client_from_params"],
)
async def test_get_user_from_superuser(
    async_client_from_params: AsyncClient, status_code: int, user_id: int
) -> None:
    response = await async_client_from_params.get(f"/v1/users/{user_id}")
    assert response.status_code == status_code

    if response.status_code == 200:
        response_json = response.json()
        assert response_json["id"] == user_id


@pytest.mark.parametrize(
    "async_client_from_params,status_code,user_id,new_email,new_password,role",
    [
        (
            {"email": "user2@example.com", "password": "user1"},
            401,
            None,
            None,
            None,
            None,
        ),
        (
            {"email": "user3example.com", "password": "user2"},
            401,
            None,
            None,
            None,
            None,
        ),
        (
            {"email": "user2@example.com", "password": "user2"},
            403,
            None,
            None,
            None,
            None,
        ),
        (
            {"email": "owner2@example.com", "password": "owner2"},
            403,
            None,
            None,
            None,
            None,
        ),
        (
            {"email": "admin@example.com", "password": "admin"},
            404,
            10,
            "new_user2@example.com",
            "new_user2",
            "user",
        ),
        (
            {"email": "admin@example.com", "password": "admin"},
            200,
            6,
            "new_user2@example.com",
            "new_user2",
            "user",
        ),
    ],
    indirect=["async_client_from_params"],
)
async def test_update_user_from_superuser(
    async_client_from_params: AsyncClient,
    status_code: int,
    user_id: int,
    new_email: str,
    new_password: str,
    role: str,
) -> None:
    response = await async_client_from_params.put(
        f"/v1/users/{user_id}",
        json={"email": new_email, "password": new_password, "role": role},
    )
    assert response.status_code == status_code

    if response.status_code == 200:
        response_json = response.json()
        assert response_json["email"] == new_email
        # undo changes
        await async_client_from_params.put(
            f"/v1/users/{user_id}",
            json={
                "email": new_email.lstrip("_new"),
                "password": new_password.lstrip("_new"),
                "role": role,
            },
        )


@pytest.mark.parametrize(
    "async_client_from_params,status_code,user_id,email,password,role",
    [
        (
            {"email": "user2@example.com", "password": "user1"},
            401,
            None,
            None,
            None,
            None,
        ),
        (
            {"email": "user3example.com", "password": "user2"},
            401,
            None,
            None,
            None,
            None,
        ),
        (
            {"email": "user2@example.com", "password": "user2"},
            403,
            None,
            None,
            None,
            None,
        ),
        (
            {"email": "owner2@example.com", "password": "owner2"},
            403,
            None,
            None,
            None,
            None,
        ),
        (
            {"email": "admin@example.com", "password": "admin"},
            404,
            10,
            "user2@example.com",
            "user2",
            "user",
        ),
        (
            {"email": "admin@example.com", "password": "admin"},
            200,
            6,
            "user2@example.com",
            "user2",
            "user",
        ),
    ],
    indirect=["async_client_from_params"],
)
async def test_delete_user_from_superuser(
    async_client_from_params: AsyncClient,
    status_code: int,
    user_id: int,
    email: str,
    password: str,
    role: str,
) -> None:
    response = await async_client_from_params.delete(f"/v1/users/{user_id}")
    assert response.status_code == status_code

    if response.status_code == 200:
        response_json = response.json()
        assert response_json["email"] == email
        assert response_json["id"] == user_id
        # undo changes
        await async_client_from_params.post(
            "/v1/auth/register",
            json={"email": email, "password": password, "role": role},
        )
