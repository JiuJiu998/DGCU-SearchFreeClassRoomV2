# app/schemas.py
from datetime import datetime, time
from typing import Optional, List

from pydantic import BaseModel


# ======== 通用基类 ========
class ORMBase(BaseModel):
    class Config:
        orm_mode = True


# ======== Setting ========
class SettingBase(BaseModel):
    value: str


class SettingCreate(SettingBase):
    key: str


class SettingUpdate(SettingBase):
    pass


class Setting(SettingBase, ORMBase):
    key: str


# ======== BuildingGroup ========
class BuildingGroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class BuildingGroupCreate(BuildingGroupBase):
    pass


class BuildingGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class BuildingGroup(BuildingGroupBase, ORMBase):
    id: int


# ======== ClassRoom ========
class ClassRoomBase(BaseModel):
    building: str
    floor: str
    room_no: str
    is_room: bool
    room_size: str
    all_socket: bool
    comment: Optional[str] = None
    group_id: int


class ClassRoomCreate(ClassRoomBase):
    pass


class ClassRoomUpdate(BaseModel):
    building: Optional[str] = None
    floor: Optional[str] = None
    room_no: Optional[str] = None
    is_room: Optional[bool] = None
    room_size: Optional[str] = None
    all_socket: Optional[bool] = None
    comment: Optional[str] = None
    group_id: Optional[int] = None


class ClassRoom(ClassRoomBase, ORMBase):
    id: int


# ======== Section ========
class SectionBase(BaseModel):
    code: str
    description: Optional[str] = None


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None


class Section(SectionBase, ORMBase):
    id: int


# ======== SectionTime ========
class SectionTimeBase(BaseModel):
    section_id: int
    group_id: int
    start_time: time
    end_time: time


class SectionTimeCreate(SectionTimeBase):
    pass


class SectionTimeUpdate(BaseModel):
    section_id: Optional[int] = None
    group_id: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class SectionTime(SectionTimeBase, ORMBase):
    id: int


# ======== ScheduleEntry ========
class ScheduleEntryBase(BaseModel):
    week: int
    weekday: int
    section_id: int
    room_id: int
    course_name: Optional[str] = None
    class_name: Optional[str] = None
    raw: Optional[str] = None


class ScheduleEntryCreate(ScheduleEntryBase):
    pass


class ScheduleEntryUpdate(BaseModel):
    week: Optional[int] = None
    weekday: Optional[int] = None
    section_id: Optional[int] = None
    room_id: Optional[int] = None
    course_name: Optional[str] = None
    class_name: Optional[str] = None
    raw: Optional[str] = None


class ScheduleEntry(ScheduleEntryBase, ORMBase):
    id: int


# ======== User ========
class UserBase(BaseModel):
    wxopen_id: str


class UserCreate(UserBase):
    pass


class User(UserBase, ORMBase):
    id: int


# ======== Tag ========
class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None


class Tag(TagBase, ORMBase):
    id: int


# ======== RoomTag（行为记录） ========
class RoomTagBase(BaseModel):
    week: int
    weekday: int
    section_id: int
    room_id: int
    user_id: int
    tag_id: int


class RoomTagCreate(RoomTagBase):
    """一次创建一个节次的占用，可在前端循环调用"""
    pass


class RoomTagBulkCreate(BaseModel):
    """一次占用多个节次：section_ids 列表"""
    week: int
    weekday: int
    section_ids: List[int]
    room_id: int
    user_id: int
    tag_id: int


class RoomTag(RoomTagBase, ORMBase):
    id: int
    created_at: datetime
