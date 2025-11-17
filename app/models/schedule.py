# app/models/schedule.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classroom.id"))
    week = Column(Integer, index=True)
    day = Column(Integer, index=True)       # 1-7
    section = Column(String(10), index=True)  # 0102, 0304...

    classroom = relationship("Classroom")
