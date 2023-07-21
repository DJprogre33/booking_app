from app.models.users import Users
from app.utils.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = Users
