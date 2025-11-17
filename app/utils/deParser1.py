import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple

from utils import save_json_to_file


def parse_weeks_and_location(lines: List[str]) -> List[Tuple[str, str]]:
    """
    从给定的行列表中解析出周次和地点的组合
    返回格式: [(周次1, 地点1), (周次2, 地点2), ...]
    """
    # 预编译正则表达式，提高效率
    week_pattern = re.compile(r'\(([^)]*周)\)')
    separator_pattern = re.compile(r'-{5,}')

    results = []
    current_weeks = None
    current_location = None
    skip_next = False

    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue

        # 检测分隔符
        if separator_pattern.match(line):
            # 遇到分隔符时提交当前组合
            if current_weeks and current_location:
                for loc in current_location.split(','):
                    if loc.strip():
                        results.append((current_weeks, loc.strip()))
            current_weeks = None
            current_location = None
            continue

        # 尝试匹配周次
        week_match = week_pattern.search(line)
        if week_match:
            # 找到周次信息
            current_weeks = week_match.group(1)  # 去掉括号

            # 检查下一行是否可能是地点
            if i + 1 < len(lines) and not separator_pattern.match(lines[i + 1]):
                next_line = lines[i + 1]
                # 排除明显不是地点的行
                if not week_pattern.search(next_line) and not any(char in next_line for char in ['(', ')', '教师', '班级']):
                    current_location = next_line
                    skip_next = True  # 跳过下一行，因为已作为地点使用
            continue

        # 如果当前没有周次但找到可能是地点的行
        if not current_weeks and current_location is None:
            # 排除明显不是地点的行
            if (not week_pattern.search(line) and
                    not any(char in line for char in ['(', ')', '教师', '班级']) and
                    not line.startswith(',')):
                current_location = line

    # 处理最后一个组合
    if current_weeks and current_location:
        for loc in current_location.split(','):
            if loc.strip():
                results.append((current_weeks, loc.strip()))

    return results


def parse_course_table_from_html2(file_path: str) -> List[Dict]:
    # 加载 HTML 文件
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", id="timetable")
    if not table:
        raise ValueError("未找到 id='timetable' 的表格")

    rows = table.find_all("tr")[2:]  # 前两行是表头，跳过

    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    sections = ["0102", "0304", "0506", "0708", "0910", "1112"]

    results = []

    for row in rows:
        cells = row.find_all("td")
        for index, cell in enumerate(cells[1:-1]):  # 跳过首尾
            if cell.text.strip() == "":
                continue
            weekday_index = index // 6
            section_index = index % 6

            # 解析每个 <div class="kbcontent1">
            divs = BeautifulSoup(cell.decode_contents(), "html.parser").find_all("div", class_="kbcontent1")
            for div in divs:
                text = div.get_text(separator="\n").strip()
                lines = [line.strip() for line in text.splitlines() if line.strip()]

                # 确保有足够的信息
                if len(lines) < 2:
                    continue

                course_name = lines[0]
                class_name = lines[1]

                # 解析周次和地点
                week_location_pairs = parse_weeks_and_location(lines[2:])

                # 如果没有解析到周次和地点，尝试使用整个lines
                if not week_location_pairs:
                    week_location_pairs = parse_weeks_and_location(lines)

                # 为每个(周次, 地点)对创建记录
                for weeks, location in week_location_pairs:
                    results.append({
                        "weekDay": weekdays[weekday_index],
                        "section": sections[section_index],
                        "courseName": course_name,
                        "className": class_name,
                        "weeks": weeks,
                        "classRoom": location
                    })

                # 如果没有解析到任何组合，但仍需记录课程信息
                if not week_location_pairs:
                    results.append({
                        "weekDay": weekdays[weekday_index],
                        "section": sections[section_index],
                        "courseName": course_name,
                        "className": class_name,
                        "weeks": "未知周次",
                        "classRoom": "未知地点"
                    })

    return results


def validate_parsing_results(results: List[Dict]) -> None:
    """
    自动验证解析结果并生成报告
    """
    # 统计解析状态
    status_counts = {"success": 0, "missing_weeks": 0, "missing_location": 0}

    # 收集问题数据
    problems = []

    for record in results:
        # 检查关键字段
        week_issue = record["weeks"] in ["未知周次", ""]
        location_issue = record["classRoom"] in ["未知地点", ""]

        if week_issue and location_issue:
            status_counts["missing_weeks"] += 1
            status_counts["missing_location"] += 1
            problems.append(("both", record))
        elif week_issue:
            status_counts["missing_weeks"] += 1
            problems.append(("weeks", record))
        elif location_issue:
            status_counts["missing_location"] += 1
            problems.append(("location", record))
        else:
            status_counts["success"] += 1

    # 生成验证报告
    total = len(results)
    success_rate = (status_counts["success"] / total) * 100 if total > 0 else 0

    print("=" * 50)
    print("解析结果验证报告")
    print("=" * 50)
    print(f"总记录数: {total}")
    print(f"成功解析: {status_counts['success']} ({success_rate:.2f}%)")
    print(f"缺失周次: {status_counts['missing_weeks']}")
    print(f"缺失地点: {status_counts['missing_location']}")
    print("-" * 50)

    # 显示典型问题示例
    if problems:
        print("问题记录示例:")
        for issue_type, record in problems[:3]:  # 只显示前3个示例
            print(f"类型: {issue_type}")
            print(f"原始数据: {record.get('rawLines', [])}")
            print(f"解析结果: 周次={record['weeks']}, 地点={record['classRoom']}")
            print("-" * 50)

        # 保存完整问题记录到文件
        with open("parsing_problems.json", "w", encoding="utf-8") as f:
            json.dump(problems, f, ensure_ascii=False, indent=2)
        print(f"完整问题记录已保存至: parsing_problems.json")
    else:
        print("所有记录解析成功!")


def validate_with_patterns(results: List[Dict]):
    """
    使用正则模式验证关键字段格式
    """
    # 周次模式：如 "1-16周"、"1,3,5周" 等
    week_pattern = re.compile(r".*周$")

    # 地点模式：至少包含数字或字母，长度至少为2
    location_pattern = re.compile(r".*[a-zA-Z0-9].{1,}")

    valid_count = 0
    invalid_records = []

    for record in results:
        weeks_valid = bool(week_pattern.match(record["weeks"])) if record["weeks"] else False
        location_valid = bool(location_pattern.match(record["classRoom"])) if record["classRoom"] else False

        if weeks_valid and location_valid:
            valid_count += 1
        else:
            invalid_records.append({
                "record": record,
                "weeks_valid": weeks_valid,
                "location_valid": location_valid
            })

    print(f"格式验证结果: {valid_count}/{len(results)} 条记录符合格式要求")

    if invalid_records:
        print("问题记录示例:")
        for record_info in invalid_records[:3]:
            rec = record_info["record"]
            print(f"课程: {rec['courseName']}")
            print(f"周次: {rec['weeks']} ({'有效' if record_info['weeks_valid'] else '无效'})")
            print(f"地点: {rec['classRoom']} ({'有效' if record_info['location_valid'] else '无效'})")
            print("-" * 50)


def check_data_consistency(results: List[Dict]):
    """
    检查数据一致性（如同一时间同一地点是否有冲突）
    """
    # 创建时间-地点映射
    time_location_map = {}
    conflicts = []

    for record in results:
        key = (record["weekDay"], record["section"], record["classRoom"])

        # 忽略未知地点
        if record["classRoom"] in ["未知地点", ""]:
            continue

        if key in time_location_map:
            # 检查周次是否有重叠
            existing_weeks = time_location_map[key]["weeks"]
            new_weeks = record["weeks"]

            # 简单检查是否有相同周次（实际应更复杂）
            if existing_weeks == new_weeks:
                conflicts.append({
                    "location": key[2],
                    "time": f"{key[0]} {key[1]}节",
                    "existing": time_location_map[key],
                    "new": record
                })
        else:
            time_location_map[key] = record

    if conflicts:
        print(f"发现 {len(conflicts)} 个潜在时间冲突:")
        for conflict in conflicts[:3]:  # 只显示前3个
            print(f"冲突地点: {conflict['location']}")
            print(f"冲突时间: {conflict['time']}")
            print(f"现有课程: {conflict['existing']['courseName']} ({conflict['existing']['weeks']}周)")
            print(f"新课程: {conflict['new']['courseName']} ({conflict['new']['weeks']}周)")
            print("-" * 50)
    else:
        print("未发现时间地点冲突")


res = parse_course_table_from_html2("kebiao.html")
print(type(res))
print(len(res))

# 转为 JSON 字符串
json_str = json.dumps(res, ensure_ascii=False, indent=2)

# 保存到文件
save_json_to_file(json_str, "table 2025-09-08.json")