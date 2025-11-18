import json
import re
from bs4 import BeautifulSoup
from app.utils.ParserResult import ParserResult
from app.utils.test import parse_weeks


def format_classrooms(classrooms):
    formatted = []

    for room in classrooms:
        room = room.replace('、', ',')  # 中文逗号改英文
        room = room.replace('-------', '')  # 去掉多余 -
        room = room.strip()
        if not room:
            continue

        # 匹配前缀和编号，例如 5B201,202 或 8C405,406
        m = re.match(r'([0-9A-Z]+)([\d,]+)(.*)', room)
        if m:
            prefix, numbers, suffix = m.groups()
            numbers_list = re.split(r',', numbers)
            full_rooms = [prefix + n for n in numbers_list]
            if suffix:
                # 机房后缀
                full_rooms = [r + suffix for r in full_rooms]
            formatted.append(','.join(full_rooms))
        else:
            formatted.append(room)

    return formatted


# 正则仅提取 "(xxx周)"
week_pattern = re.compile(r'\([^()]*?周\)')

WEEKDAY_MAP = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
SECTION_MAP = ["0102", "0304", "0506", "0708", "0910", "1112"]

results = []
week_styles = set()
room_styles = set()

with open("kebiao.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

table = soup.find("table")
tbody = table.find("tbody") or table

for row_idx, tr in enumerate(tbody.find_all("tr")):
    tds = tr.find_all("td")

    for col_idx, td in enumerate(tds):
        blocks = td.find_all("div", class_="kbcontent1")
        if not blocks or col_idx == 0:
            continue

        weekday = WEEKDAY_MAP[(col_idx - 1) // 6]
        section = SECTION_MAP[(col_idx - 1) % 6]

        for block in blocks:
            # 原始行（保留顺序）
            raw_lines = block.get_text("\n", strip=False).split("\n")

            # 1️⃣ 预处理：合并纯标点行到上一行，避免生成 room_no 为 ","
            merged_lines = []
            for ln in raw_lines:
                stripped = ln.strip()
                if stripped in [",", "，", ";", "；"] or re.fullmatch(r'^[^\w\u4e00-\u9fff]+$', stripped):
                    if merged_lines:
                        merged_lines[-1] = merged_lines[-1].rstrip() + stripped
                    else:
                        continue
                else:
                    merged_lines.append(ln)

            # 2️⃣ 清洗：把只含空白或分隔符的行变为 "" 以便统一判断
            lines = [ln.strip() if ln and ln.strip() != "-------" else "" for ln in merged_lines]

            n = len(lines)
            if n == 0:
                continue

            # 找出所有包含周次的行索引
            week_line_idxs = [i for i, ln in enumerate(lines) if ln and week_pattern.search(ln)]
            if not week_line_idxs:
                continue

            # 合并连续的周次行为一个组
            groups = []
            start = week_line_idxs[0]
            prev = start
            for idx in week_line_idxs[1:]:
                if idx == prev + 1:
                    prev = idx
                    continue
                else:
                    groups.append((start, prev))
                    start = idx
                    prev = idx
            groups.append((start, prev))

            # 上一次解析出的上下文（用于“单独周次行继承上文”的情况）
            last_course = None
            last_class = None
            last_teacher = None

            for (g_start, g_end) in groups:
                # 收集该组内所有括号内容（按行顺序）
                week_list = []
                for j in range(g_start, g_end + 1):
                    matches = week_pattern.findall(lines[j])
                    if matches:
                        week_list.extend(matches)

                if not week_list:
                    continue

                # 3️⃣ 向后找 room_no
                room_no = None
                for j in range(g_end + 1, n):
                    cand = lines[j]
                    if not cand:
                        continue
                    if week_pattern.search(cand):
                        continue
                    if re.fullmatch(r'^[^\w\u4e00-\u9fff]+$', cand):
                        continue
                    room_no = cand
                    break

                # 4️⃣ 向前回溯最多4行作为 course/class/teacher
                course = None
                classname = None
                teacher = None
                back_count = 0
                j = g_start - 1
                collected = []
                while j >= 0 and back_count < 4:
                    if lines[j]:
                        if week_pattern.search(lines[j]):
                            break
                        collected.append(lines[j])
                    j -= 1
                    back_count += 1
                collected = collected[::-1]

                if collected:
                    if len(collected) >= 2:
                        course = collected[0]
                        classname = collected[1]
                    else:
                        course = collected[0]

                # g_start 行可能同时包含老师名
                first_week_line = lines[g_start]
                teacher_candidate = re.sub(r'\([^()]*\)', '', first_week_line).strip()
                if teacher_candidate:
                    teacher = teacher_candidate

                # 继承上一个 group 的 course/class/teacher
                if course is None:
                    course = last_course
                if classname is None:
                    classname = last_class
                if teacher is None:
                    teacher = last_teacher

                # 回退策略：从整个块中找第一个合理的非周次行
                if room_no is None:
                    for cand in lines:
                        if not cand:
                            continue
                        if week_pattern.search(cand):
                            continue
                        if re.fullmatch(r'^[^\w\u4e00-\u9fff]+$', cand):
                            continue
                        room_no = cand
                        break

                if not room_no:
                    continue

                week_text = " , ".join(week_list)

                last_course = course
                last_class = classname
                last_teacher = teacher

                pr = ParserResult(
                    building=None,
                    floor=None,
                    room_no=room_no,
                    section=section,
                    week=week_text,
                    weekday=weekday
                )
                results.append(pr)
                week_styles.add(week_text)
                room_styles.add(room_no)

# ================== 输出统计 ==================
print("============== 解析结果统计 ==============")
print("成功解析课程记录数:", len(results))
print("周次样式种类数:", len(week_styles))
print("教室样式种类数:", len(room_styles))
print("=========================================\n")

print("\n【所有周次样式】")
for w in sorted(week_styles):
    print("-"*50)
    print(w)
    print("周次解析结果:", parse_weeks(w))


print("\n【所有教室样式】")
for r in sorted(room_styles):
    print(r)

print("\n=========== 示例 ParserResult 前20条 ===========")
for r in results[:20]:
    r.show()
    print("------------------------------------")


white_room_no_dict = [
    {'area': "7号楼A区", "origin": "7号楼A"},
    {'area': "7号楼B区", "origin": "7号楼B"},
    {'area': "7号楼C区", "origin": "7号楼C"},
    {'area': "羽毛球场", "origin": "综合馆-羽毛球场"}
]

# 构建白名单前缀和完全匹配集合
prefix_whitelist = [w['origin'] for w in white_room_no_dict if w['origin'] != w['area']]
exact_whitelist = [w['area'] for w in white_room_no_dict]

# 构建 origin -> area 的映射，方便赋值 building
origin_area_map = {w['origin']: w['area'] for w in white_room_no_dict}
area_exact_map = {w['area']: w['area'] for w in white_room_no_dict}

filtered_results = []

for result in results:
    rooms = result.room_no.split(',')
    valid_rooms = []
    for r in rooms:
        r = r.strip()
        if "-------" in r:
            continue

        # 如果 r 是数字或缩写（例如 113），则补全前缀
        if re.match(r'^\d+$', r):
            if valid_rooms:
                # 继承前一个房间号的前缀（去掉后面的数字部分）
                prefix = re.match(r'^(.*?)[0-9]+$', valid_rooms[-1]).group(1)
                r = prefix + r

        # 检查白名单
        matched_area = None
        if any(r.startswith(p) for p in prefix_whitelist):
            for p in prefix_whitelist:
                if r.startswith(p):
                    matched_area = origin_area_map[p]
                    break
        elif r in exact_whitelist:
            matched_area = area_exact_map[r]

        if matched_area:
            valid_rooms.append(r)
            result.building = matched_area

            # floor 解析：ABC 后面的第一个数字
            m = re.match(r'.*?[ABC](\d)', r)
            if m:
                result.floor = int(m.group(1))
            else:
                result.floor = 1  # 羽毛球场等特殊区域默认1楼

    if valid_rooms:
        result.room_no = ','.join(valid_rooms)
        filtered_results.append(result)

results = filtered_results


# ================= 写入 JSON ===================
output_path = "parsed_results.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump([r.to_dict() for r in results], f, ensure_ascii=False, indent=4)

print(f"\n🎉 已成功写入 JSON 文件：{output_path}")
print(f"总记录数: {len(results)}")



