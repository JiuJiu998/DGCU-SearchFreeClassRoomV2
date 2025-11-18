import re
from bs4 import BeautifulSoup
from app.utils.allTypes.ParserResult import ParserResult

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
            lines = block.get_text("\n", strip=True).split("\n")

            temp_weeks = []

            for line in lines:
                line = line.strip()
                if not line or line == "-------":
                    continue

                has_week = week_pattern.search(line)

                if has_week:
                    # 发现多个"(xxx周)"同行 → 全部合并
                    matches = week_pattern.findall(line)
                    temp_weeks.extend(matches)
                else:
                    # 当前行不含周次且已有周次 → 本行为room_no
                    if temp_weeks:
                        room_no = line
                        week_text = " , ".join(temp_weeks)

                        week_styles.add(week_text)
                        room_styles.add(room_no)

                        pr = ParserResult(
                            building=None,
                            floor=None,
                            room_no=room_no,
                            section=section,
                            week=week_text,
                            weekday=weekday
                        )
                        results.append(pr)

                        temp_weeks.clear()

print("============== 解析结果统计 ==============")
print("成功解析课程记录数:", len(results))
print("周次样式种类数:", len(week_styles))
print("教室样式种类数:", len(room_styles))
print("=========================================\n")

print("\n【所有周次样式】")
for w in sorted(week_styles):
    print(w)

print("\n【所有教室样式】")
for r in sorted(room_styles):
    print(r)

print("\n=========== 示例 ParserResult 前20条 ===========")
for r in results[:20]:
    r.show()
    print("------------------------------------")
