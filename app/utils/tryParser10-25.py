import re
from bs4 import BeautifulSoup
from app.utils.allTypes.ParserResult import ParserResult

week_pattern = re.compile(r'\([^()]*?周\)')

WEEKDAY_MAP = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
SECTION_MAP = ["0102", "0304", "0506", "0708", "0910", "1112"]

results = []
week_styles = set()
room_styles = set()
errors = []

with open("kebiao.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

table = soup.find("table")
tbody = table.find("tbody") or table  # fallback

for row_idx, tr in enumerate(tbody.find_all("tr")):
    tds = tr.find_all("td")

    for col_idx, td in enumerate(tds):
        blocks = td.find_all("div", class_="kbcontent1")
        if not blocks:
            continue

        if col_idx == 0:  # 第一列课程名
            continue

        weekday = WEEKDAY_MAP[(col_idx - 1) // 6]
        section = SECTION_MAP[(col_idx - 1) % 6]

        for block in blocks:
            lines = block.get_text("\n", strip=True).split("\n")

            temp_weeks = []
            room_no = None

            for line in lines:
                line = line.strip()

                if not line or line == "-------":
                    continue

                week_matches = week_pattern.findall(line)

                if week_matches:
                    temp_weeks.extend(week_matches)
                    continue

                # 非“周)”行且已有周次 → 为教室
                if temp_weeks:
                    room_no = line
                    room_styles.add(room_no)
                    for week in temp_weeks:
                        week_styles.add(week)

                        pr = ParserResult(
                            building=None,
                            floor=None,
                            room_no=room_no,
                            section=section,
                            week=week,
                            weekday=weekday
                        )
                        results.append(pr)

                    temp_weeks.clear()

print("=============== 解析统计 ===============")
print("成功解析课程数量：", len(results))
print("发现周次样式数量：", len(week_styles))
print("发现教室样式数量：", len(room_styles))
print("=====================================\n")

print("【周次样式列表】")
for w in sorted(week_styles):
    print(w)

print("\n【教室样式列表】")
for r in sorted(room_styles):
    print(r)

# 打印前20条便于检查
print("\n=========== 示例 ParserResult 前20条 ===========")
for r in results[:20]:
    r.show()
    print("------------------------------------")
