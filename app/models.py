from sqlalchemy.dialects.mysql import ENUM
from enum import Enum as PyEnum

from sqlalchemy.orm import relationship

from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, UniqueConstraint, Time, ForeignKey, Enum, Text


class RoomSize(PyEnum):
    BIG = "BIG"
    MID = "MID"
    SMALL = "SMALL"


class Setting(Base):
    __tablename__ = "settings"
    key = Column(String(100), primary_key=True)
    value = Column(String(255), nullable=False)  # 不能为空


# ===================== 教室分组（时间分区） =====================
class BuildingGroup(Base):
    __tablename__ = "building_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)  # 如 Group A、Group B
    description = Column(String(255), nullable=True)  # 可存楼栋列表描述

    rooms = relationship("ClassRoom", back_populates="group")


# ===================== 教室 =====================
class ClassRoom(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    building = Column(String(255), nullable=False)
    floor = Column(String(255), nullable=False)
    room_no = Column(String(255), nullable=False)
    is_room = Column(Boolean, nullable=False)
    room_size = Column(Enum(RoomSize, name="room_size_enum"), nullable=False)
    all_socket = Column(Boolean, nullable=False)
    comment = Column(String(255), nullable=True)

    group_id = Column(Integer, ForeignKey("building_groups.id"), nullable=False)

    group = relationship("BuildingGroup", back_populates="rooms")

    __table_args__ = (
        UniqueConstraint('building', 'floor', 'room_no', name='uq_room_location'),
    )


# ===================== 节次定义（仅节次序号，不含时间） =====================
class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)


# ===================== 每个楼栋分组的节次时间表 =====================
class SectionTime(Base):
    __tablename__ = "section_times"

    id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("building_groups.id"), nullable=False)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    __table_args__ = (
        UniqueConstraint("section_id", "group_id", name="uq_section_group"),
    )


class ScheduleEntry(Base):
    __tablename__ = "schedule_entries"

    id = Column(Integer, primary_key=True)
    week = Column(Integer, index=True)
    weekday = Column(Integer, index=True)

    # 通过节次ID关联 Section 表 (更规范)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)

    # 关联教室
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)

    # 课程信息
    course_name = Column(String(255), nullable=True)
    class_name = Column(String(255), nullable=True)

    # 原始爬取内容存档
    raw = Column(Text, nullable=True)

    section = relationship("Section")
    room = relationship("ClassRoom")

    # 同一课不可重复 同一节次同一时间同意教室不可能有两个数据
    __table_args__ = (
        UniqueConstraint(
            "week", "weekday", "section_id", "room_id",
            name="uix_sched_unique"
        ),
    )


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    wxopen_id = Column(String(255), unique=True, nullable=False)  # 唯一非空微信小程序用户ID


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)  # 唯一非空Tag标签


class RoomTag(Base):
    __tablename__ = "room_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 时间维度 (与 ScheduleEntry 对齐)
    week = Column(Integer, nullable=False)
    weekday = Column(Integer, nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)

    # 关联对象
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)

    # 数据自动清理关键字段
    expire_at = Column(DateTime, nullable=False)

    # 关系映射
    user = relationship("User")
    room = relationship("ClassRoom")
    tag = relationship("Tag")
    section = relationship("Section")

    # 一个用户同一节次只能占用一间教室
    __table_args__ = (
        UniqueConstraint(
            "user_id", "week", "weekday", "section_id",
            name="uq_user_only_one_room_in_section"
        ),
    )
