# app/routers/admin.py
import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi._compat.may_v1 import BaseModel

from app import schemas, crud, models
from app.dependencies import verify_modify_key
from fastapi import UploadFile, File
import pandas as pd
from sqlalchemy.orm import Session
from app.models import ClassRoom, Section, ScheduleEntry
from app.database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(verify_modify_key)],  # 整个 router 都需要密钥
)


# ======== Settings ========
@router.put("/settings", response_model=schemas.Setting)
def upsert_setting(setting_in: schemas.SettingCreate, db: Session = Depends(get_db)):
    return crud.upsert_setting(db, setting_in)


@router.delete("/settings/{key}")
def delete_setting(key: str, db: Session = Depends(get_db)):
    crud.delete_setting(db, key)
    return {"ok": True}


@router.post("/import-schedules")
async def import_schedule(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
):
    """
    上传 class_test.json 并写入 schedule_entries 表（带详细错误打印）
    """
    # 读取 JSON
    try:
        data = json.loads((await file.read()).decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JSON 解析失败：{e}")

    inserted = 0
    skipped = 0
    errors = 0

    for idx, item in enumerate(data):

        week = item.get("week")
        weekday = item.get("weekday")
        section_code = item.get("section")
        building = item.get("building")
        floor = item.get("floor")
        room_no = item.get("room_no")

        # ✨ 打印字段缺失错误
        if not (week and weekday and section_code and building and room_no):
            errors += 1
            print(f"[错误#{errors}] 记录 index={idx} 缺少必要字段 → {item}")
            continue

        # 查 section
        section = db.query(Section).filter(Section.code == section_code).first()
        if not section:
            errors += 1
            print(
                f"[错误#{errors}] index={idx} section 不存在: section={section_code} → 原始数据: {item}"
            )
            continue

        # 楼层映射字典
        FLOOR_MAP = {
            1: "一楼",
            2: "二楼",
            3: "三楼",
            4: "四楼",
            5: "五楼",
            6: "六楼"
        }

        # 查找教室
        room = db.query(ClassRoom).filter(
            ClassRoom.building == building,
            ClassRoom.floor == FLOOR_MAP.get(floor, None),
            ClassRoom.room_no == room_no
        ).first()

        # 羽毛球场特殊逻辑
        if not room and building == "羽毛球场":
            room = db.query(ClassRoom).filter(
                ClassRoom.building == "羽毛球场",
                ClassRoom.room_no == "综合馆-羽毛球场"
            ).first()

        if not room:
            errors += 1
            print(
                f"[错误#{errors}] index={idx} 找不到教室: building={building}, floor={floor}, room_no={room_no} → {item}"
            )
            continue

        # 唯一性 check
        exists = db.query(ScheduleEntry).filter(
            ScheduleEntry.week == week,
            ScheduleEntry.weekday == weekday,
            ScheduleEntry.section_id == section.id,
            ScheduleEntry.room_id == room.id
        ).first()

        if exists:
            skipped += 1
            print(
                f"[跳过#{skipped}] index={idx} 重复课表: week={week}, weekday={weekday}, "
                f"section={section_code}, room_id={room.id} → {item}"
            )
            continue

        # 插入
        entry = ScheduleEntry(
            week=week,
            weekday=weekday,
            section_id=section.id,
            room_id=room.id
        )
        db.add(entry)
        inserted += 1
    # -------------------------
    # ✨✨ 新增：自动清理未安排教室
    # -------------------------

    # SQL：将 rooms 中未被 schedule_entries 用到的教室自动标记为无效
    cleanup_sql = """
        UPDATE rooms r
        LEFT JOIN schedule_entries se ON r.id = se.room_id
        SET 
            r.is_room = 0,
            r.comment = '课表未安排，自动去除'
        WHERE
            r.is_room = 1
            AND se.room_id IS NULL;
    """

    db.execute(cleanup_sql)
    db.commit()
    db.close()

    return {
        "message": "课程表导入完成",
        "inserted": inserted,
        "skipped": skipped,
        "errors": errors,
        "total": len(data)
    }



@router.post("/import-rooms")
async def import_rooms(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        # modify_key: str = Depends(verify_modify_key),  # <-- 修正点！
):
    import io
    import pandas as pd

    # 验证文件格式
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400,
                            detail="只支持 .xlsx 文件导入")

    # Read file as binary into BytesIO
    content = await file.read()
    df = pd.read_excel(io.BytesIO(content))  # 修复点！

    # 楼栋分组配置
    group_map = {
        "A": 1, "图书": 1, "综合": 1, "室外": 1, "羽毛球": 1,
        "B": 2, "C": 2, "3号": 2, "5号": 2, "8号": 2,
    }

    def detect_group(building: str) -> int:
        for key, gid in group_map.items():
            if key in building:
                return gid
        raise HTTPException(
            status_code=400,
            detail=f"楼栋 '{building}' 未匹配到分组，请检查数据或更新分组规则"
        )

    size_map = {"大": "BIG", "中": "MID", "小": "SMALL"}
    yes_map = {"是": True, "否": False, "教室": True, "非教室": False}

    imported = 0
    updated = 0

    for _, row in df.iterrows():
        building = str(row["教学楼"]).strip()
        floor = str(row["楼层"]).strip()
        room_no = str(row["教室号"]).strip()

        group_id = detect_group(building)

        data = {
            "building": building,
            "floor": floor,
            "room_no": room_no,
            "is_room": yes_map.get(str(row["是否教室"]).strip(), False),
            "room_size": size_map.get(str(row["教室尺寸"]).strip(), "MID"),
            "all_socket": yes_map.get(str(row["独立插座"]).strip(), False),
            "comment": str(row.get("备注")).strip() if row.get("备注") else None,
            "group_id": group_id,
        }

        room = db.query(models.ClassRoom).filter_by(
            building=building, floor=floor, room_no=room_no
        ).first()

        if room:
            for k, v in data.items():
                setattr(room, k, v)
            updated += 1
        else:
            db.add(models.ClassRoom(**data))
            imported += 1

    db.commit()

    return {
        "imported": imported,
        "updated": updated,
        "total": imported + updated,
        "message": "成功导入教室数据并自动匹配楼栋分组"
    }


# ======== BuildingGroups ========
@router.post("/building-groups", response_model=schemas.BuildingGroup)
def create_building_group(
        obj_in: schemas.BuildingGroupCreate, db: Session = Depends(get_db)
):
    return crud.create_building_group(db, obj_in)


@router.put("/building-groups/{group_id}", response_model=schemas.BuildingGroup)
def update_building_group(
        group_id: int, obj_in: schemas.BuildingGroupUpdate, db: Session = Depends(get_db)
):
    obj = crud.update_building_group(db, group_id, obj_in)
    if not obj:
        raise HTTPException(status_code=404, detail="BuildingGroup not found")
    return obj


@router.delete("/building-groups/{group_id}")
def delete_building_group(group_id: int, db: Session = Depends(get_db)):
    crud.delete_building_group(db, group_id)
    return {"ok": True}

# ======== ClassRooms / Sections / SectionTimes / ScheduleEntries / Tags ========
# 这里你可以按同样模式继续加：
# - POST /rooms
# - PUT /rooms/{id}
# - DELETE /rooms/{id}
# - POST /sections ...
# - POST /section-times ...
# - POST /schedule-entries ...
# - POST /tags ...
