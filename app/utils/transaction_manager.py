from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.repositories.auths import AuthsRepository
from app.repositories.bookings import BookingsRepository
from app.repositories.hotels import HotelsRepository
from app.repositories.rooms import RoomsRepository
from app.repositories.users import UsersRepository


class ITransactionManager(ABC):
    auth: AuthsRepository
    users: UsersRepository
    rooms: RoomsRepository
    hotels: HotelsRepository
    bookings: BookingsRepository
    session: AsyncSession

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError


class TransactionManager(ITransactionManager):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()
        self.users = UsersRepository(self.session)
        self.auth = AuthsRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.hotels = HotelsRepository(self.session)
        self.bookings = BookingsRepository(self.session)

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
