import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(ENUM("user", "hotel owner", "admin", name="role", create_type=True))

    bookings = relationship("Bookings", back_populates="users")

    def __str__(self):
        return f"User #{self.email}"


class RefreshSessions(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    refresh_token: Mapped[uuid.UUID] = mapped_column(UUID, index=True)
    expires_in: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.utcnow())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
