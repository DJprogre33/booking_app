"""
Since the user repository does not have its own functions,
this file tests the SQLAlchemy repository's basic functions.
"""

import pytest

from app.models.users import Users
from app.utils.auth import get_password_hash
from app.utils.transaction_manager import ITransactionManager


@pytest.mark.parametrize(
    "user_id,email,exists",
    [
        (1, "user1@example.com", True),
        (2, "user2@example.com", True),
        (3, "owner1@example.com", True),
        (4, "owner2@example.com", True),
        (5, "admin@example.com", True),
        (5, "unknownemail@test.com", False),
    ],
)
async def test_users_find_one_or_none(
    user_id: int, email: str, exists: bool, transaction_manager: ITransactionManager
) -> None:
    async with transaction_manager:
        user = await transaction_manager.users.find_one_or_none(email=email)
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
        ("admin", 1, ("admin@example.com",)),
    ],
)
async def test_users_find_all(
    role: str, total: int, emails: tuple, transaction_manager: ITransactionManager
) -> None:
    async with transaction_manager:
        users = await transaction_manager.users.find_all(role=role)
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
async def test_insert_data(
    email: str, password: str, role: str, transaction_manager: ITransactionManager
) -> None:
    async with transaction_manager:
        new_user = await transaction_manager.users.insert_data(
            email=email, hashed_password=get_password_hash(password), role=role
        )
        # check how SQLAlchemy returning function works
        assert isinstance(new_user, Users)
        assert new_user.email == email
        assert new_user.role == role
        await transaction_manager.rollback()


@pytest.mark.parametrize(
    "user_id,new_email,new_role,exists",
    [
        (1, "updated_user1@example.com", "hotel owner", True),
        (3, "updated_owner1@example.com", "user", True),
        (6, "updated_unknown@example.com", "user", False),
    ],
)
async def test_update_fields_by_id(
    user_id: int,
    new_email: str,
    new_role: str,
    exists: bool,
    transaction_manager: ITransactionManager,
) -> None:
    async with transaction_manager:
        user = await transaction_manager.users.find_one_or_none(id=user_id)
        if exists:
            original_email, original_role = user.email, user.role
            updated_user = await transaction_manager.users.update_fields_by_id(
                entity_id=user_id, email=new_email, role=new_role
            )
            assert updated_user.email != original_email
            assert updated_user.role != original_role

            assert updated_user.email == new_email
            assert updated_user.role == new_role
        else:
            assert not user
        await transaction_manager.rollback()


@pytest.mark.parametrize(
    "user_id,exists", [(1, True), (2, True), (3, True), (6, False)]
)
async def test_delete(
    user_id: int, transaction_manager: ITransactionManager, exists: bool
) -> None:
    async with transaction_manager:
        deleted_user = await transaction_manager.users.delete(id=user_id)
        if exists:
            assert deleted_user.id == user_id
            assert not await transaction_manager.users.find_one_or_none(
                id=deleted_user.id
            )
        else:
            assert not deleted_user


@pytest.mark.parametrize(
    "offset,limit,total_users",
    [(0, 1, 1), (0, 5, 5), (0, 10, 5), (5, 5, 0), (4, 5, 1), (2, 2, 2)],
)
async def test_get_users_list(
    offset: int, limit: int, total_users: int, transaction_manager: ITransactionManager
) -> None:
    async with transaction_manager:
        users = await transaction_manager.users.get_users_list(
            offset=offset, limit=limit
        )
        assert len(users) == total_users
