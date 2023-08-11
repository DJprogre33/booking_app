from typing import Any, Optional, Union

from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Hotels(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="owner_id", ondelete="CASCADE")
    )
    name: Mapped[str]
    location: Mapped[str]
    services: Mapped[dict[str, Any]]
    rooms_quantity: Mapped[int]
    image_path: Mapped[Optional[str]]

    rooms = relationship("Rooms", back_populates="hotels")

    def __str__(self):
        return f"id: {self.id}, name: {self.name}"
