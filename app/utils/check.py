from bs4 import BeautifulSoup

with open("kebiao.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

week_set = set()
room_set = set()

blocks = soup.find_all("div", class_="kbcontent1")

for block in blocks:
    lines = block.get_text("\n", strip=True).split("\n")

    for i, line in enumerate(lines):
        if "周)" in line:
            week = line.strip()
            # 下一行必定是 room_no
            if i + 1 < len(lines):
                room = lines[i + 1].strip()
            else:
                room = None

            week_set.add(week)
            room_set.add(room)

print("-------- 周次格式 --------")
for w in sorted(week_set):
    print(repr(w))

print("\n-------- 教室格式 --------")
for r in sorted(room_set):
    print(repr(r))

print("\n周次格式种类数量：", len(week_set))
print("教室格式种类数量：", len(room_set))
print("kbcontent1 总数量：", len(blocks))
