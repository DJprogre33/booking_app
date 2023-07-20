from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(ENUM("user", "hotel owner", "admin", name="role", create_type=True))

    bookings = relationship("Bookings", back_populates="users")

    def __str__(self):
        return f"User #{self.email}"
