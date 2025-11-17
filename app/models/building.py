from sqlalchemy import Column, Integer, String

from app.core.database import Base, TimestampMixin


class Building(Base, TimestampMixin):
    __tablename__ = 'building'
    id = Column(Integer, primary_key=True, autoincrement=True)      # 自增主键
    building_name = Column(String(255), index=True, unique=True)     # 索引唯一

