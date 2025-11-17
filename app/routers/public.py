# app/routers/public.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import schemas, crud, models

router = APIRouter(prefix="/api", tags=["public"])


# ======== 基础查询 ========

@router.get("/building-groups", response_model=list[schemas.BuildingGroup])
def list_building_groups(db: Session = Depends(get_db)):
    return crud.get_building_groups(db)


@router.get("/rooms", response_model=list[schemas.ClassRoom])
def list_rooms(db: Session = Depends(get_db)):
    return crud.get_rooms(db)


@router.get("/sections", response_model=list[schemas.Section])
def list_sections(db: Session = Depends(get_db)):
    return crud.get_sections(db)


@router.get("/tags", response_model=list[schemas.Tag])
def list_tags(db: Session = Depends(get_db)):
    return crud.get_tags(db)


# ======== 小程序用户注册 / 获取 ========
@router.post("/users", response_model=schemas.User)
def register_or_get_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_or_create_user(db, payload.wxopen_id)
    return user


# ======== 房间打 Tag ========

@router.post("/room-tags", response_model=list[schemas.RoomTag])
def bulk_set_room_tags(
    payload: schemas.RoomTagBulkCreate,
    db: Session = Depends(get_db),
):
    """一次占用多个节次（0102、0304、0506等），前端传 section_ids 列表"""
    # TODO: 此处可加业务判断（是否与课程表冲突 / 是否该节次教室已被授课占用等）
    objs = crud.bulk_create_roomtags(db, payload)
    return objs


@router.get(
    "/room-tags/{week}/{weekday}/{section_id}/{room_id}",
    response_model=list[schemas.RoomTag],
)
def get_room_tags_for_room_and_time(
    week: int,
    weekday: int,
    section_id: int,
    room_id: int,
    db: Session = Depends(get_db),
):
    return crud.get_roomtags_for_room_and_time(db, week, weekday, section_id, room_id)


@router.delete("/room-tags/{roomtag_id}")
def remove_room_tag(roomtag_id: int, db: Session = Depends(get_db)):
    crud.delete_roomtag(db, roomtag_id)
    return {"ok": True}
