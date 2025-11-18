import re
from bs4 import BeautifulSoup
from app.utils.allTypes.ParserResult import ParserResult

week_pattern = re.compile(r'\([^()]*?周\)')  # 捕获最小匹配 "(…周)"

WEEKDAY_MAP = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
SECTION_MAP = ["0102", "0304", "0506", "0708", "0910", "1112"]

results = []
week_styles = set()
room_styles = set()

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

        if col_idx == 0:
            continue

        weekday = WEEKDAY_MAP[(col_idx - 1) // 6]
        section = SECTION_MAP[(col_idx - 1) % 6]

        for block in blocks:
            lines = block.get_text("\n", strip=True).split("\n")

            for i, line in enumerate(lines):
                if "周)" not in line:
                    continue

                week_matches = week_pattern.findall(line)
                if not week_matches:
                    continue

                if i + 1 >= len(lines):
                    continue

                room_no = lines[i + 1].strip()
                room_styles.add(room_no)

                for week in week_matches:
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


# 输出解析统计
print("\n==============解析统计==============")
print("成功解析课程数量:", len(results))
print("周次样式数量:", len(week_styles))
print("教室样式数量:", len(room_styles))
print("====================================\n")

# 打印所有 week 类型
print("【所有周次格式】")
for w in sorted(week_styles):
    print(w)

print("\n【所有教室格式】")
for r in sorted(room_styles):
    print(r)

# 打印前 10 条结果验证
print("\n=========== 示例 ParserResult 前10条 ===========")
for r in results[:10]:
    r.show()
    print("------------------------------------")
