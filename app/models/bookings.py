from datetime import date

from sqlalchemy import Computed, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Bookings(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    date_from: Mapped[date]
    date_to: Mapped[date]
    price: Mapped[int]
    total_cost: Mapped[int] = mapped_column(Computed("(date_to - date_from) * price"))
    total_days: Mapped[int] = mapped_column(Computed("date_to - date_from"))

    users = relationship("Users", back_populates="bookings")
    rooms = relationship("Rooms", back_populates="bookings")

    def __str__(self):
        return f"Booking #{self.id}"
