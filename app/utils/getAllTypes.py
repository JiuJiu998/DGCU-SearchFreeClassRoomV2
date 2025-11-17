import pandas as pd
from collections import Counter, defaultdict

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

# 统计
length_counter = Counter()
example_data = defaultdict(list)

for i in range(df.shape[0]):
    course_name = df.iloc[i, 0]

    for wd_index, wd in enumerate(weekdays):
        start_col = 1 + wd_index * 6
        end_col = start_col + 6
        week_data = df.iloc[i, start_col:end_col].tolist()

        for period, cell in zip(periods, week_data):
            if not pd.isna(cell):
                items = cell.split(' ')
                length = len(items)
                length_counter[length] += 1

                # 只存一个示例
                if len(example_data[length]) < 1:
                    example_data[length].append(items)

# 输出统计结果
print("长度统计：")
for length, count in length_counter.items():
    print(f"长度 {length}: 出现 {count} 次，示例数据: {example_data[length][0]}")
