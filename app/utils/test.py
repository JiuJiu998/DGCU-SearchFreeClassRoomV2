import json
from collections import defaultdict

# 修改为你的文件路径
FILE_PATH = "class_test.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_duplicates(data):
    seen = defaultdict(list)
    duplicates = []

    for idx, item in enumerate(data):

        # 唯一键（使用section_code 而不是 section_id，因为是纯脚本）
        key = (
            item.get("week"),
            item.get("weekday"),
            item.get("section"),
            item.get("building"),
            item.get("floor"),
            item.get("room_no"),
        )

        seen[key].append(idx)

    # 提取出现次数>1 的 key
    for key, indices in seen.items():
        if len(indices) > 1:
            duplicates.append((key, indices))

    return duplicates


if __name__ == "__main__":
    data = load_json(FILE_PATH)
    duplicates = find_duplicates(data)

    if not duplicates:
        print("✔ 没有发现重复记录")
    else:
        print(f"⚠ 发现 {len(duplicates)} 组重复记录：\n")
        for (key, indices) in duplicates:
            (week, weekday, section, building, floor, room_no) = key
            print(f"🔁 重复：week={week}, weekday={weekday}, section={section}, "
                  f"building={building}, floor={floor}, room_no={room_no}")
            print(f"    → 出现在 JSON 中的记录序号（从 0 开始）：{indices}\n")
