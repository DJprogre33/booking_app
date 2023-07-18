import pytest
from app.users.dao import UsersDAO


@pytest.mark.parametrize(
    "user_id,email,exists",
    [
        (1, "test@test.com", True),
        (2, "artem@example.com", True),
        (3, "unknownemail@test.com", False)
    ]
)
async def test_user_find_one_or_none(user_id: int, email: str, exists: bool):
    user = await UsersDAO.find_one_or_none(id=user_id)

    if exists:
        assert user.id == user_id
        assert user.email == email
    else:
        assert not user
