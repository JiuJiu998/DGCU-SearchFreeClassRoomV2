import pandas as pd

from app.utils.allTypes.ParserResult import ParserResult

def parse_index_cells(index, cells, weekday, section):
    results = []
    used = set()

    for i in range(len(index)):
        if i in used:
            continue

        x = index[i]
        pair_found = False

        # 尝试找 y
        for j in range(i + 1, len(index)):
            y = index[j]

            if y == x + 1 or y == x + 2:
                # 合并两段周次
                weeks = cells[x] + cells[y]

                # 教室位置在下一个
                room_no = cells[y + 1] if (y + 1 < len(cells)) else None

                pr = ParserResult(
                    building=None,
                    floor=None,
                    room_no=room_no,
                    section=section,
                    week=weeks,
                    weekday=weekday
                )
                results.append(pr)

                used.add(i)
                used.add(j)
                pair_found = True
                break

        if not pair_found:
            # 单独 weeks
            weeks = cells[x]
            room_no = cells[x + 1] if (x + 1 < len(cells)) else None

            pr = ParserResult(
                building=None,
                floor=None,
                room_no=room_no,
                section=section,
                week=weeks,
                weekday=weekday
            )
            results.append(pr)
            used.add(i)

    return results



# 读取 HTML
with open("kebiao.html", "r", encoding="utf-8") as f:
    html = f.read()

tables = pd.read_html(html)
df = tables[0]

# 忽略第一行
df = df.iloc[1:, :].reset_index(drop=True)

# 课程名列
course_col = df.columns[0]

# 星期和节次
weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
periods = ["0102", "0304", "0506", "0708", "0910", "1112"]

results = []

# 遍历课程
for i in range(df.shape[0]):
    course_name = df.iloc[i, 0]
    # print(f"课程: {course_name}")

    # 遍历星期
    for wd_index, wd in enumerate(weekdays):
        # print(f"  {wd}:")
        # 计算这一星期的数据列索引
        start_col = 1 + wd_index * 6
        end_col = start_col + 6
        week_data = df.iloc[i, start_col:end_col].tolist()

        # 遍历节次
        for period, cell in zip(periods, week_data):
            # print(f"    {period}: {cell}")
            # 星期wd,节次period,单元格cell
            if not pd.isna(cell):
                weekday = wd
                section = period
                # 只针对非空
                index = []
                cells = cell.split(' ')
                # 找到列表中 所有 周) 的位置索引，如果其中有两个 周) 的位置只差一个且为',' 说明是同一节次，要合并周次 如果不为',' 说明后面一个应该是教室位置，此时1个 周) 对应一个教室位置
                for i in range(0, len(cells)):
                    if "周)" in cells[i]:
                        index.append(i)
                parsed = parse_index_cells(index, cells, wd, period)

                for item in parsed:
                    print(item)
                    item.show()
                    print("--"*25)
                    results.append(item)
                print(cells)
                print(index)
print(results)
print(len(results))
