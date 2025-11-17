import pandas as pd
from collections import Counter, defaultdict

# 读取 HTML
with open("kebiao.html", "r", encoding="utf-8") as f:
    html = f.read()

tables = pd.read_html(html)
df = tables[0]

# 忽略第一行
df = df.iloc[1:, :].reset_index(drop=True)

# 定义星期与节次
weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
periods = ["0102", "0304", "0506", "0708", "0910", "1112"]

# 用于统计 index 类型（元组形式）
index_pattern_counter = Counter()
index_pattern_examples = defaultdict(list)

# 遍历课程
for i in range(df.shape[0]):

    for wd_index, wd in enumerate(weekdays):
        start_col = 1 + wd_index * 6
        end_col = start_col + 6
        week_data = df.iloc[i, start_col:end_col].tolist()

        for period, cell in zip(periods, week_data):
            if not pd.isna(cell):
                cells = cell.split(' ')

                # 生成 index 列表
                indices = []
                for j in range(len(cells)):
                    if "周)" in cells[j]:
                        indices.append(j)

                # 转为元组
                index_tuple = tuple(indices)

                # 计数
                index_pattern_counter[index_tuple] += 1

                # 保存示例（每种类型保留 3 个）
                if len(index_pattern_examples[index_tuple]) < 3:
                    index_pattern_examples[index_tuple].append(cells)

# 输出统计
print("\n=== 所有 index 模式统计 ===")
for pattern, count in index_pattern_counter.items():
    print(f"模式 {pattern}：共 {count} 次")
    print("  示例：")
    for ex in index_pattern_examples[pattern]:
        print("    ", ex)
    print()
