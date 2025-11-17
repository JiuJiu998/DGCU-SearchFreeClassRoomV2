# app/models/classroom.py

from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base


class Classroom(Base):
    __tablename__ = "classroom"

    id = Column(Integer, primary_key=True, index=True)
    building = Column(String(50), index=True)
    floor = Column(String(20))
    room_id = Column(String(20))
    is_classroom = Column(Boolean, default=True)
