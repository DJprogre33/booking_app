import asyncio
import json
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import insert

from app.config import settings
from app.database import Base, async_session_maker, engine
from app.main import app as fastapi_app
from app.models.bookings import Bookings
from app.models.hotels import Hotels
from app.models.rooms import Rooms
from app.models.users import Users


async def create_async_client(login_data):
    """Function which create async client"""
    async with AsyncClient(app=fastapi_app, base_url="http://test") as async_client:
        email, password = login_data["email"], login_data["password"]
        await async_client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        # assert async_client.cookies["booking_access_token"]

        yield async_client


@pytest.fixture(scope="module", autouse=True)
async def prepare_database():
    """Prepare Database for testing"""

    assert settings.MODE == "TEST"

    # drop and create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", encoding="UTF-8") as file:
            return json.load(file)

    # loading mock data
    users = open_mock_json("users")
    hotels = open_mock_json("hotels")
    rooms = open_mock_json("rooms")
    bookings = open_mock_json("bookings")

    for booking in bookings:
        booking["date_from"] = datetime.strptime(booking["date_from"], "%Y-%m-%d")
        booking["date_to"] = datetime.strptime(booking["date_to"], "%Y-%m-%d")

    # insert data
    async with async_session_maker() as session:
        add_users = insert(Users).values(users)
        add_hotels = insert(Hotels).values(hotels)
        add_rooms = insert(Rooms).values(rooms)
        add_bookings = insert(Bookings).values(bookings)

        await session.execute(add_users)
        await session.execute(add_hotels)
        await session.execute(add_rooms)
        await session.execute(add_bookings)

        await session.commit()


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="session")
async def auth_async_client(request):
    default_email = "user1@example.com"
    default_password = "user1"

    login_data = {"email": default_email, "password": default_password}

    async for async_client in create_async_client(login_data):
        yield async_client


@pytest.fixture(scope="function")
async def async_client_from_params(request):
    login_data = request.param
    async for async_client in create_async_client(login_data):
        yield async_client
