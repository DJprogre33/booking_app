from app.models.users import RefreshSessions
from app.utils.repository import SQLAlchemyRepository


class AuthsRepository(SQLAlchemyRepository):
    model = RefreshSessions
