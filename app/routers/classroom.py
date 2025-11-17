# app/routers/classroom.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.classroom import Classroom
from app.models.schedule import Schedule
from typing import List

router = APIRouter(prefix="/classroom", tags=["Classroom"])


@router.get("/free")
def get_free_classroom(
    week: int,
    day: int,
    section: str,
    building: str,
    floor: str,
    db: Session = Depends(get_db)
):
    # 所有教室
    query = db.query(Classroom).filter(
        Classroom.building == building,
        Classroom.floor == floor,
    )

    # 查询已被占用的教室
    busy = db.query(Schedule.classroom_id).filter(
        Schedule.week == week,
        Schedule.day == day,
        Schedule.section == section
    )

    # 未被占用 → 空教室
    free_rooms = query.filter(
        ~Classroom.id.in_(busy)
    ).all()

    return free_rooms
