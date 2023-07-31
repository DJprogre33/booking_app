"""
Since the user repository does not have its own functions,
this file tests the SQLAlchemy repository's basic functions.
"""

import pytest

from app.auth.auth import get_password_hash, verify_password
from app.exceptions import IncorrectIDException
from app.models.users import Users
from app.repositories.users import UsersRepository


# repository for user query
tasks_repo = UsersRepository


@pytest.mark.parametrize(
    "user_id,email,exists",
    [
        (1, "user1@example.com", True),
        (2, "user2@example.com", True),
        (3, "owner1@example.com", True),
        (4, "owner2@example.com", True),
        (5, "unknownemail@test.com", False),
    ],
)
async def test_user_find_one_or_none(user_id: int, email: str, exists: bool) -> None:
    user = await tasks_repo.find_one_or_none(email=email)

    if exists:
        assert user.id == user_id
        assert user.email == email
    else:
        assert not user


@pytest.mark.parametrize(
    "role, total, emails",
    [
        ("user", 2, ("user1@example.com", "user2@example.com")),
        ("hotel owner", 2, ("owner1@example.com", "owner2@example.com")),
    ],
)
async def test_user_find_all(role: str, total: int, emails: tuple) -> None:
    users = await tasks_repo.find_all(role=role)
    assert len(users) == total

    for user in users:
        assert user.email in emails


@pytest.mark.parametrize(
    "email,password,role",
    [
        ("user3@example.com", "user3", "user"),
        ("hotel3@example.com", "hotel3", "hotel owner"),
    ],
)
async def test_insert_data(email: str, password: str, role: str) -> None:
    new_user = await tasks_repo.insert_data(
        email=email, hashed_password=get_password_hash(password), role=role
    )
    # check how SQLAlchemy returning function works
    assert isinstance(new_user, Users)
    assert new_user.email == email
    assert new_user.role == role

    # get created user by email
    new_user = await tasks_repo.find_one_or_none(email=email)

    assert isinstance(new_user, Users)
    assert new_user.email == email
    assert new_user.role == role
    assert verify_password(password, new_user.hashed_password)


@pytest.mark.parametrize(
    "user_id,new_email,new_role",
    [
        (5, "delete_user3@example.com", "hotel owner"),
        (6, "delete_owner3@example.com", "user"),
        (7, "delete_owner3@example.com", "user"),
    ],
)
async def test_update_fields_by_id(user_id: int, new_email: str, new_role: str) -> None:
    current_user = await tasks_repo.find_one_or_none(id=user_id)

    # if id not found raise error
    if user_id == 7:
        with pytest.raises(IncorrectIDException):
            await tasks_repo.update_fields_by_id(
                entity_id=user_id, email=new_email, role=new_role
            )
    else:
        updated_user = await tasks_repo.update_fields_by_id(
            entity_id=user_id, email=new_email, role=new_role
        )
        assert updated_user.email != current_user.email
        assert updated_user.role != current_user.role

        assert updated_user.email == new_email
        assert updated_user.role == new_role


@pytest.mark.parametrize("user_id", [5, 6, 7])
async def test_delete_by_id(user_id: int) -> None:
    # if id not found raise error
    if user_id == 7:
        with pytest.raises(IncorrectIDException):
            await tasks_repo.delete_by_id(user_id)
    else:
        deleted_user_id = await tasks_repo.delete_by_id(user_id)
        assert deleted_user_id == user_id

        user = await tasks_repo.find_one_or_none(id=user_id)
        assert not user
