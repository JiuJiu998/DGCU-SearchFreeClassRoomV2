# app/crud.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas


# ======== Setting ========
def get_setting(db: Session, key: str) -> Optional[models.Setting]:
    return db.query(models.Setting).filter(models.Setting.key == key).first()


def upsert_setting(db: Session, setting_in: schemas.SettingCreate) -> models.Setting:
    db_obj = get_setting(db, setting_in.key)
    if db_obj:
        db_obj.value = setting_in.value
    else:
        db_obj = models.Setting(key=setting_in.key, value=setting_in.value)
        db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_setting(db: Session, key: str) -> None:
    obj = get_setting(db, key)
    if obj:
        db.delete(obj)
        db.commit()


# ======== BuildingGroup ========
def get_building_group(db: Session, group_id: int) -> Optional[models.BuildingGroup]:
    return db.query(models.BuildingGroup).get(group_id)


def get_building_groups(db: Session) -> List[models.BuildingGroup]:
    return db.query(models.BuildingGroup).all()


def create_building_group(db: Session, obj_in: schemas.BuildingGroupCreate) -> models.BuildingGroup:
    obj = models.BuildingGroup(**obj_in.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_building_group(db: Session, group_id: int, obj_in: schemas.BuildingGroupUpdate) -> Optional[models.BuildingGroup]:
    obj = get_building_group(db, group_id)
    if not obj:
        return None
    for field, value in obj_in.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_building_group(db: Session, group_id: int) -> None:
    obj = get_building_group(db, group_id)
    if obj:
        db.delete(obj)
        db.commit()


# ======== ClassRoom ========
def get_room(db: Session, room_id: int) -> Optional[models.ClassRoom]:
    return db.query(models.ClassRoom).get(room_id)


def get_rooms(db: Session) -> List[models.ClassRoom]:
    return db.query(models.ClassRoom).all()


def create_room(db: Session, obj_in: schemas.ClassRoomCreate) -> models.ClassRoom:
    obj = models.ClassRoom(**obj_in.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_room(db: Session, room_id: int, obj_in: schemas.ClassRoomUpdate) -> Optional[models.ClassRoom]:
    obj = get_room(db, room_id)
    if not obj:
        return None
    for field, value in obj_in.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_room(db: Session, room_id: int) -> None:
    obj = get_room(db, room_id)
    if obj:
        db.delete(obj)
        db.commit()


# ======== Section / SectionTime / ScheduleEntry（同套路） ========
def get_section(db: Session, section_id: int) -> Optional[models.Section]:
    return db.query(models.Section).get(section_id)


def get_sections(db: Session) -> List[models.Section]:
    return db.query(models.Section).all()


def create_section(db: Session, obj_in: schemas.SectionCreate) -> models.Section:
    obj = models.Section(**obj_in.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_section(db: Session, section_id: int, obj_in: schemas.SectionUpdate) -> Optional[models.Section]:
    obj = get_section(db, section_id)
    if not obj:
        return None
    for field, value in obj_in.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_section(db: Session, section_id: int) -> None:
    obj = get_section(db, section_id)
    if obj:
        db.delete(obj)
        db.commit()


# 你可以按上述模式再写：
# - SectionTime 的增删改查
# - ScheduleEntry 的增删改查
# - Tag 的增删改查


# ======== User（小程序用户，允许无密钥创建） ========
def get_user_by_openid(db: Session, wxopen_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.wxopen_id == wxopen_id).first()


def get_or_create_user(db: Session, wxopen_id: str) -> models.User:
    user = get_user_by_openid(db, wxopen_id)
    if user:
        return user
    user = models.User(wxopen_id=wxopen_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ======== Tag（定义） ========
def get_tag(db: Session, tag_id: int) -> Optional[models.Tag]:
    return db.query(models.Tag).get(tag_id)


def get_tags(db: Session) -> List[models.Tag]:
    return db.query(models.Tag).all()


def create_tag(db: Session, obj_in: schemas.TagCreate) -> models.Tag:
    obj = models.Tag(**obj_in.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_tag(db: Session, tag_id: int, obj_in: schemas.TagUpdate) -> Optional[models.Tag]:
    obj = get_tag(db, tag_id)
    if not obj:
        return None
    for field, value in obj_in.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_tag(db: Session, tag_id: int) -> None:
    obj = get_tag(db, tag_id)
    if obj:
        db.delete(obj)
        db.commit()


# ======== RoomTag（打 Tag 行为） ========
def create_roomtag(db: Session, obj_in: schemas.RoomTagCreate) -> models.RoomTag:
    obj = models.RoomTag(
        week=obj_in.week,
        weekday=obj_in.weekday,
        section_id=obj_in.section_id,
        room_id=obj_in.room_id,
        user_id=obj_in.user_id,
        tag_id=obj_in.tag_id,
        created_at=datetime.utcnow(),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def bulk_create_roomtags(db: Session, obj_in: schemas.RoomTagBulkCreate) -> List[models.RoomTag]:
    result = []
    for sid in obj_in.section_ids:
        rt_in = schemas.RoomTagCreate(
            week=obj_in.week,
            weekday=obj_in.weekday,
            section_id=sid,
            room_id=obj_in.room_id,
            user_id=obj_in.user_id,
            tag_id=obj_in.tag_id,
        )
        result.append(create_roomtag(db, rt_in))
    return result


def get_roomtags_for_room_and_time(
    db: Session, week: int, weekday: int, section_id: int, room_id: int
) -> List[models.RoomTag]:
    return (
        db.query(models.RoomTag)
        .filter(
            models.RoomTag.week == week,
            models.RoomTag.weekday == weekday,
            models.RoomTag.section_id == section_id,
            models.RoomTag.room_id == room_id,
        )
        .all()
    )


def delete_roomtag(db: Session, roomtag_id: int) -> None:
    obj = db.query(models.RoomTag).get(roomtag_id)
    if obj:
        db.delete(obj)
        db.commit()
