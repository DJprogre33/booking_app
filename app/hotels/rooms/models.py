from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class Rooms(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, nullable=False)
    hotel_id = Column(ForeignKey("hotels.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    services = Column(JSON, nullable=False)
    quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)

    bookings = relationship("Bookings", back_populates="rooms")
    hotels = relationship("Hotels", back_populates="rooms")

    def __str__(self):
        return f"id: {self.id} name: {self.name}"
