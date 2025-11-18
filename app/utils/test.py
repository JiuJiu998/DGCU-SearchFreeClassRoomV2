import re


def parse_weeks(weeks_str):
    """解析周次字符串，返回周次列表"""
    weeks_parse_failed_counter = 0
    cleaned = re.sub(r'[()周]', '', weeks_str)
    cleaned = cleaned.replace("单周", "").replace("双周", "")
    periods = re.split(r'[,，]', cleaned)

    week_list = []
    for period in periods:
        period = period.strip()
        if not period:
            continue
        if '-' in period:
            try:
                start, end = map(int, period.split('-'))
                week_list.extend(range(start, end + 1))
            except:
                weeks_parse_failed_counter += 1
                continue
        elif period.isdigit():
            week_list.append(int(period))
        elif '单' in period or '双' in period:
            try:
                week_num = int(re.sub(r'[单双]', '', period))
                week_list.append(week_num)
            except:
                weeks_parse_failed_counter += 1
                continue
        else:
            weeks_parse_failed_counter += 1
            continue
    return sorted(set(week_list))


