from app.utils.repository import SQLAlchemyRepository
from app.models.users import RefreshSessions


class AuthsRepository(SQLAlchemyRepository):
    model = RefreshSessions
