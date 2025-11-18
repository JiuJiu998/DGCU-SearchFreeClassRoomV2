from bs4 import BeautifulSoup

def count_theoretical_groups(html_path="kebiao.html"):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    blocks = soup.find_all("div", class_="kbcontent1")

    total_groups = 0
    per_block = []  # 可选：查看每块多少组

    for block in blocks:
        text = block.get_text("\n", strip=True)

        # 基本一组
        group_count = 1

        # 每出现一次“-------”就多一组
        group_count += text.count("-------")

        total_groups += group_count
        per_block.append(group_count)

    print("========== 理论应解析组数统计 ==========")
    print(f"kbcontent1 块总数：{len(blocks)}")
    print(f"每块组数：{per_block}")
    print(f"理论总组数（应生成 ParserResult 数量）：{total_groups}")
    print("=========================================\n")

    return total_groups


theoretical = count_theoretical_groups("kebiao.html")

print("理论应有数量:", theoretical)
