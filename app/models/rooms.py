from typing import Any, Optional, Union

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Rooms(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"))
    name: Mapped[str]
    description: Mapped[Optional[str]]
    price: Mapped[int]
    services: Mapped[dict[str, Any]]
    quantity: Mapped[int]
    image_path: Mapped[Optional[str]]

    bookings = relationship("Bookings", back_populates="rooms")
    hotels = relationship("Hotels", back_populates="rooms")

    def __str__(self):
        return f"id: {self.id} name: {self.name}"
