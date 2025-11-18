from bs4 import BeautifulSoup

with open("kebiao.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# 找 table
table = soup.find("table")
tbody = table.find("tbody") or table  # fallback

trs = tbody.find_all("tr")

total_kbcontent1_count = 0
non_empty_td_count = 0
first_col_count = 0

for tr in trs:
    tds = tr.find_all("td")

    if not tds:
        continue

    first_col_count += 1  # 第一列 td 数量（每一行唯一）

    for td in tds:
        # 找出所有 kbcontent1 内容块
        blocks = td.find_all("div", class_="kbcontent1")
        count = len(blocks)

        total_kbcontent1_count += count

        # 如果至少有一个 kbcontent1，则为非空单元格
        if count > 0:
            non_empty_td_count += 1

total_td_count = sum(len(tr.find_all("td")) for tr in trs)

empty_td_count = total_td_count - non_empty_td_count

print("👉 kbcontent1 内容块总数量 =", total_kbcontent1_count)
print("👉 非空单元格数量       =", non_empty_td_count)
print("👉 第一列单元格数量     =", first_col_count)
print("👉 tbody td 总数        =", total_td_count)
print("👉 空 td 数量          =", empty_td_count)
