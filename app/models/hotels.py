from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Hotels(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, nullable=False)
    owner_id = Column(ForeignKey("users.id", name="owner_id"), nullable=False)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    services = Column(JSON)
    rooms_quantity = Column(Integer, nullable=False)
    image_path = Column(String, nullable=True)

    rooms = relationship("Rooms", back_populates="hotels")

    def __str__(self):
        return f"id: {self.id}, name: {self.name}"




