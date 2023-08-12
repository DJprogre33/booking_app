import pytest
from app.utils.transaction_manager import TransactionManager
from typing import AsyncGenerator


@pytest.fixture(scope="module")
async def transaction_manager() -> AsyncGenerator:
    """Creates a transaction manager for working with Repository"""
    yield TransactionManager()
