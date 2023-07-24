import pytest

from app.repositories.users import UsersRepository


@pytest.mark.parametrize(
    "user_id,email,exists",
    [
        (1, "user1@example.com", True),
        (2, "user2@example.com", True),
        (3, "owner1@example.com", True),
        (4, "owner2@example.com", True),
        (5, "unknownemail@test.com", False)
    ]
)
async def test_user_find_one_or_none(user_id: int, email: str, exists: bool):
    user = await UsersRepository().find_one_or_none(email=email)

    if exists:
        assert user.id == user_id
        assert user.email == email
    else:
        assert not user
