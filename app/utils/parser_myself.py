import pandas as pd

from app.utils.allTypes.ParserResult import ParserResult


def parse_index_cells(index, cells, weekday, section):
    results = []
    i = 0

    while i < len(index):
        x = index[i]
        weeks = cells[x]

        # 获取教室地址
        room_no = cells[x + 1] if (x + 1 < len(cells)) else None

        j = i + 1
        # 向后检查是否可连续合并
        while j < len(index):
            y = index[j]
            # 如果 y 紧接 x 后方，并且教室一致，则合并
            next_room = cells[y + 1] if (y + 1 < len(cells)) else None
            if (y == index[j - 1] + 2) and (next_room == room_no):
                weeks += "、" + cells[y]  # 合并多个周次
                j += 1
            else:
                break

        # 生成结果
        pr = ParserResult(
            building=None,
            floor=None,
            room_no=room_no,
            section=section,
            week=weeks,
            weekday=weekday
        )
        results.append(pr)

        i = j  # 跳到下一段

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
totalNumber = 0
allNumber = 0
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
            allNumber += 1
            if not pd.isna(cell):
                totalNumber += 1
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

                print(cells)
                for item in parsed:
                    item.show()
                    results.append(item)
                    print("*" * 25)
                print('-'*50)
print(len(results))
print(allNumber)
print(totalNumber)