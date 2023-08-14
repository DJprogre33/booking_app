import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "async_client_from_params,offset,limit,status_code,total_users",
    [
        ({"email": "user2@example.com", "password": "user2"}, None, None, 403, 7),
        ({"email": "owner2@example.com", "password": "owner2"}, None, None, 403, 7),
        ({"email": "admin@example.com", "password": "admin"}, 0, 10, 200, 7),
        ({"email": "admin@example.com", "password": "admin"}, 0, 5, 200, 5),
        ({"email": "admin@example.com", "password": "admin"}, 1, 4, 200, 4)
    ],
    indirect=["async_client_from_params"]
)
async def test_get_users_list(
    status_code: int,
    total_users: int,
    offset: int,
    limit: int,
    async_client_from_params: AsyncClient
) -> None:
    responce = await async_client_from_params.get(
        "/v1/users", params={"offset": offset, "limit": limit}
    )
    assert responce.status_code == status_code

    if responce.status_code == 200:
        assert len(responce.json()) == total_users


# @pytest.mark.parametrize(
#     "async_client_from_params,status_code,email",
#     [
#         ({"email": "user3@example.com", "password": "user3"}, 200, "user3@example.com"),
#         ({"email": "user3@example.com", "password": "user2"}, 401, "user3@example.com"),
#         ({"email": "user3example.com", "password": "user2"}, 422, "user3@example.com")
#     ],
#     indirect=["async_client_from_params"]
# )
# async def test_get_me(
#     async_client_from_params: AsyncClient, status_code: int, email: str
# ) -> None:
#     response = await async_client_from_params.get("/v1/auth/me")
#     assert response.status_code == status_code
#
#     if response.status_code == 200:
#         assert response.json()["email"] == email
#
#
# @pytest.mark.parametrize(
#     "async_client_from_params,status_code",
#     [
#         ({"email": "user3@example.com", "password": "user2"}, 401),
#         ({"email": "user3@example.com", "password": "user3"}, 200),
#         ({"email": "user3@example.com", "password": "user3"}, 401),
#         ({"email": "owner3@example.com", "password": "owner2"}, 401),
#         ({"email": "owner3@example.com", "password": "owner3"}, 200),
#     ],
#     indirect=["async_client_from_params"],
# )
# async def test_delete_me(
#     async_client_from_params: AsyncClient, status_code: int
# ) -> None:
#     response = await async_client_from_params.delete("/v1/auth/me")
#     assert response.status_code == status_code
#     if status_code == 200:
#         deleted_user = await tasks_repo.find_one_or_none(
#             email="user3@example.com"
#         )
#         assert not deleted_user
