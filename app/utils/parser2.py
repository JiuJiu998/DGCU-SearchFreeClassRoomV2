import re
import json
from bs4 import BeautifulSoup

# 可保留的楼栋
VALID_BUILDINGS = ["7号楼A", "7号楼B", "7号楼C", "综合馆-羽毛球场"]

# 从教室信息抽取楼栋、楼层、教室号
def parse_room(room_raw):
    room_raw = room_raw.strip()

    # 特殊情况：综合馆-羽毛球场
    if "综合馆-羽毛球场" in room_raw:
        return "综合馆-羽毛球场", 1, "羽毛球场"

    # 普通情况：7号楼A313
    m = re.match(r"(7号楼[A-C])(\d{3})", room_raw)
    if m:
        building = m.group(1)
        room_no = m.group(2)
        floor = int(room_no[0])
        return building, floor, room_no

    return None, None, None


# 解析周次，如：
# (1-8周)
# (9周)
# (4-9,11-19周)
# (1,3,5,7,9,11单周)
# (4双周)
def parse_weeks(week_raw):
    week_raw = week_raw.replace("周", "").replace("(", "").replace(")", "").strip()

    weeks = []

    # 单双周情况
    if "单周" in week_raw:
        nums = re.findall(r"\d+", week_raw)
        return [int(x) for x in nums if int(x) % 2 == 1]

    if "双周" in week_raw:
        nums = re.findall(r"\d+", week_raw)
        return [int(x) for x in nums if int(x) % 2 == 0]

    # 常规格式：1-8,11-19
    parts = week_raw.split(",")
    for p in parts:
        if "-" in p:
            a, b = p.split("-")
            weeks.extend(list(range(int(a), int(b) + 1)))
        else:
            weeks.append(int(p))
    return weeks


# 解析每格内容
def parse_course_block(text, weekday, section):
    lines = [x.strip() for x in text.split("<br>") if x.strip()]
    if len(lines) < 4:
        return []

    course_name = lines[0]

    # 可能多个班级情况，如：
    # 计科本2022-4班
    # 计科本2022-6班
    class_names = []
    idx = 1
    while idx < len(lines) and "班" in lines[idx]:
        class_names.append(lines[idx])
        idx += 1

    # 教师
    teacher_raw = lines[idx]
    idx += 1

    # 周次
    week_raw = lines[idx]
    weeks = parse_weeks(week_raw)

    # 教室
    room_raw = lines[idx + 1]
    building, floor, room_no = parse_room(room_raw)

    # 不在保留楼栋中 → 忽略
    if building not in VALID_BUILDINGS:
        return []

    results = []
    for w in weeks:
        for cls in class_names:
            results.append({
                "course_name": course_name,
                "class_name": cls,
                "weekday": weekday,
                "section": section,
                "week": w,
                "building": building,
                "floor": floor,
                "room_no": room_no
            })
    return results


def parse_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("table", id="timetable")
    print(table)
    # 星期顺序
    weekday_map = ["", "一", "二", "三", "四", "五", "六", "日"]

    sections = ["0102", "0304", "0506", "0708", "0910", "1112"]

    all_data = []

    rows = table.find_all("tr")[2:]   # 前两行是标题

    for tr in rows:
        tds = tr.find_all("td")
        course_title = tds[0].get_text(strip=True)

        # 跳过没有课名的行
        if not course_title:
            continue

        cell_index = 1
        for wd in range(1, 8):  # 星期一到星期日
            for s in sections:
                if cell_index >= len(tds):
                    break
                td = tds[cell_index]
                cell_index += 1

                divs = td.find_all("div", class_="kbcontent1")
                for div in divs:
                    block_html = str(div).replace("<div class=\"kbcontent1\">", "").replace("</div>", "")
                    results = parse_course_block(block_html, weekday_map[wd], s)
                    all_data.extend(results)

    return all_data


if __name__ == "__main__":
    data = parse_html("kebiao.html")

    # 过滤掉 1112 节次
    data = [d for d in data if d["section"] in ["0102", "0304", "0506", "0708", "0910"]]

    print("总课程记录数：", len(data))

    with open("parsed_courses.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("已写入 parsed_courses.json")
