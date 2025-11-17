# app/models/tag.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    tag_name = Column(String(50), unique=True)


class ClassroomTag(Base):
    __tablename__ = "classroom_tag"

    id = Column(Integer, primary_key=True)
    classroom_id = Column(Integer, ForeignKey("classroom.id"))
    tag_id = Column(Integer, ForeignKey("tag.id"))
    create_time = Column(DateTime, default=datetime.utcnow)
