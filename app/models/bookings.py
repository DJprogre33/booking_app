from sqlalchemy import Column, Computed, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class Bookings(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    room_id = Column(ForeignKey("rooms.id"), nullable=False)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=True)
    price = Column(Integer, nullable=False)
    total_cost = Column(Integer, Computed("(date_to - date_from) * price"))
    total_days = Column(Integer, Computed("date_to - date_from"))

    users = relationship("Users", back_populates="bookings")
    rooms = relationship("Rooms", back_populates="bookings")

    def __str__(self):
        return f"Booking #{self.id}"
