from sqlalchemy import Column, Integer, String, func, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM, UUID, TIMESTAMP
from sqlalchemy.orm import relationship

from app.database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(ENUM("user", "hotel owner", "admin", name="role", create_type=True), nullable=False)

    bookings = relationship("Bookings", back_populates="users")

    def __str__(self):
        return f"User #{self.email}"


class RefreshSessions(Base):
    __tablename__ = "refresh_sessions"

    id = Column(Integer, primary_key=True, nullable=False)
    refresh_token = Column(UUID, index=True, nullable=False)
    expires_in = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
