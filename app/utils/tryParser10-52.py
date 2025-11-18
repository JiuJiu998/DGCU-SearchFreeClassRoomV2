import re
from bs4 import BeautifulSoup
from app.utils.allTypes.ParserResult import ParserResult

# 正则匹配 "(xxx周)" —— 精准定位周次
week_pattern = re.compile(r'\([^()]*?周\)')

WEEKDAY_MAP = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
SECTION_MAP = ["0102", "0304", "0506", "0708", "0910", "1112"]

results = []
week_styles = set()
room_styles = set()
errors = []

# 读取 HTML
with open("kebiao.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

table = soup.find("table")
tbody = table.find("tbody") or table  # fallback

for row_idx, tr in enumerate(tbody.find_all("tr")):
    tds = tr.find_all("td")

    for col_idx, td in enumerate(tds):
        blocks = td.find_all("div", class_="kbcontent1")
        if not blocks or col_idx == 0:
            continue

        # 星期与节次自动推断
        weekday = WEEKDAY_MAP[(col_idx - 1) // 6]
        section = SECTION_MAP[(col_idx - 1) % 6]

        for block in blocks:
            lines = block.get_text("\n", strip=True).split("\n")

            week_buffer = []

            for line in lines:
                line = line.strip()
                if not line or line == "-------":
                    continue

                matches = week_pattern.findall(line)

                if matches:
                    # 所有 (xxx周) 合并积累
                    week_buffer.extend(matches)
                    continue

                # 非周次行且之前累计了周次 → 此行为教室
                if week_buffer:
                    week_text = " , ".join(week_buffer)
                    room_no = line

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

                    week_buffer = []


# ========== 输出结果统计 ==========
print("\n========== 解析统计结果 ==========")
print("成功解析课程记录数：", len(m))
print("唯一周次样式数量：", len(week_styles))
print("唯一室样式数量：", len(room_styles))
print("=================================\n")

# ========== 输出所有周次样式 ==========
print("【所有周次样式】")
for w in sorted(week_styles):
    print(w)

# ========== 输出所有教室样式 ==========
print("\n【所有教室样式】")
for r in sorted(room_styles):
    print(r)

# ========== 输出解析记录样例（前20条） ==========
print("\n=========== ParserResult 前20条 ===========")
for i, r in enumerate(results[:20], start=1):
    print(f"---- 记录 #{i} ----")
    r.show()
    print("------------------------------------")

#找到7B216的所有记录
for i in results:
    if i.room_no == ",":
        i.show()
