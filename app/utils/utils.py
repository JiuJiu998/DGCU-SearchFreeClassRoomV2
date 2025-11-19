import json
import os
import re

from bs4 import BeautifulSoup

from app.models import ScheduleEntry
from app.utils.ParserResult import ParserResult
import base64
import time

import ddddocr

from app.config import WEB_ACCOUNT, WEB_PASSWORD
import requests
from lxml import etree


# 正则仅提取 "(xxx周)"
week_pattern = re.compile(r'\([^()]*?周\)')

SECTION_MAP = ["0102", "0304", "0506", "0708", "0910", "1112"]


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


class ScheduleParser:
    def __init__(self, html_name):
        pass
        self.html_name = html_name
        self.results: [ScheduleEntry] = []
        self.html_results: [ParserResult] = []
        self.white_room_dict: [ParserResult] = []

    def parser_html(self):
        print("开始解析html")
        results: [ParserResult] = []
        # TODO: 解析HTML文件为基本的results结果，此结果未拓展周次、未拓展教室，为基本结果
        if os.path.isfile(self.html_name):
            with open(self.html_name, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
        else:
            exit(f"找不到:{self.html_name}")

        table = soup.find("table")
        tbody = table.find("tbody") or table

        for rox_idx, tr in enumerate(tbody.find_all("tr")):
            tds = tr.find_all("td")

            for col_idx, td in enumerate(tds):
                blocks = td.find_all("div", class_="kbcontent1")
                if not blocks or col_idx == 0:
                    continue

                weekday = ((col_idx - 1) // 6) + 1  # 使用1~7代表周一到周日
                section = SECTION_MAP[(col_idx - 1) % 6]

                for block in blocks:
                    # 原始行数据
                    raw_lines = block.get_text("\n", strip=False).split("\n")
                    # 1、合并纯标点行到上一行
                    merged_lines = []
                    for ln in raw_lines:
                        stripped = ln.strip()
                        if stripped in [",", "，", ";", "；"] or re.fullmatch(r'^[^\w\u4e00-\u9fff]+$', stripped):
                            if merged_lines:
                                merged_lines[-1] = merged_lines[-1].rstrip() + stripped
                            else:
                                continue
                        else:
                            merged_lines.append(ln)

                    # 2、把只含空白或者分割符号的行变成 “" 以便统一判断，针对不同周次不同教室的课程
                    lines = [ln.strip() if ln and ln.strip() != "-------" else "" for ln in merged_lines]

                    n = len(lines)

                    if n == 0:
                        continue

                    # 找出所有包含周次的行的索引
                    week_line_idxs = [i for i, ln in enumerate(lines) if ln and week_pattern.search(ln)]
                    if not week_line_idxs:
                        continue    # 所有行都没有包含周次的

                    # 合并连续的周次为一个组
                    groups = []
                    start = week_line_idxs[0]
                    prev = start
                    for idx in week_line_idxs[1:]:
                        if idx == prev + 1:
                            prev = idx
                            continue
                        else:
                            groups.append((start, prev))
                            start = idx
                            prev = idx
                    groups.append((start, prev))

                    for (g_start, g_end) in groups:
                        # 收集该组内所有括号内容（按行顺序）
                        week_list = []
                        for j in range(g_start, g_end + 1):
                            matches = week_pattern.findall(lines[j])
                            if matches:
                                week_list.extend(matches)

                        if not week_list:
                            continue

                        # 3、向后找 room_no
                        room_no = None
                        for j in range(g_end + 1, n):
                            cand = lines[j]
                            if not cand:
                                continue
                            if week_pattern.search(cand):
                                continue
                            if re.fullmatch(r'^[^\w\u4e00-\u9fff]+$', cand):
                                continue
                            room_no = cand
                            break

                        # 回退策略：从整个块中找第一个合理的非周次行
                        if room_no is None:
                            for cand in lines:
                                if not cand:
                                    continue
                                if week_pattern.search(cand):
                                    continue
                                if re.fullmatch(r'^[^\w\u4e00-\u9fff]+$', cand):
                                    continue
                                room_no = cand
                                break

                        if not room_no:
                            continue

                        week_text = " , ".join(week_list)

                        pr = ParserResult(
                            building=None,
                            floor=None,
                            room_no=room_no,
                            section=section,
                            week=week_text,
                            weekday=weekday,
                        )
                        results.append(pr)

        self.html_results = results
        print("解析结果共计:", len(self.html_results))

    def filter_white_rooms(self):
        # TODO: 构建building白名单，只保留目标building数据，并从room_no中解析出building和floor赋值
        print("开始构建白名单区域")
        white_room_no_dict = [
            {'area': "7号楼A区", "origin": "7号楼A"},
            {'area': "7号楼B区", "origin": "7号楼B"},
            {'area': "7号楼C区", "origin": "7号楼C"},
            {'area': "羽毛球场", "origin": "综合馆-羽毛球场"}
        ]
        # 构建白名单前缀和完全匹配集合
        prefix_whitelist = [w['origin'] for w in white_room_no_dict if w['origin'] != w['area']]
        exact_whitelist = [w['area'] for w in white_room_no_dict]

        # 构建 origin -> area 的映射，方便赋值 building
        origin_area_map = {w['origin']: w['area'] for w in white_room_no_dict}
        area_exact_map = {w['area']: w['area'] for w in white_room_no_dict}
        filtered_results = []

        for result in self.html_results:
            rooms = result.room_no.split(',')
            valid_rooms = []
            for r in rooms:
                r = r.strip()
                if "-------" in r:
                    continue

                # 如果 r 是数字或缩写（例如 113），则补全前缀
                if re.match(r'^\d+$', r):
                    if valid_rooms:
                        # 继承前一个房间号的前缀（去掉后面的数字部分）
                        prefix = re.match(r'^(.*?)[0-9]+$', valid_rooms[-1]).group(1)
                        r = prefix + r

                # 检查白名单
                matched_area = None
                if any(r.startswith(p) for p in prefix_whitelist):
                    for p in prefix_whitelist:
                        if r.startswith(p):
                            matched_area = origin_area_map[p]
                            break
                elif r in exact_whitelist:
                    matched_area = area_exact_map[r]

                if matched_area:
                    valid_rooms.append(r)
                    result.building = matched_area

                    # floor 解析：ABC 后面的第一个数字
                    m = re.match(r'.*?[ABC](\d)', r)
                    if m:
                        result.floor = int(m.group(1))
                    else:
                        result.floor = 1  # 羽毛球场等特殊区域默认1楼

            if valid_rooms:
                result.room_no = ','.join(valid_rooms)
                filtered_results.append(result)

        self.white_room_dict = filtered_results
        print(f"解析结果共计:{len(self.white_room_dict)}")

    def expand_weeks_rooms(self):
        """
        将 ParserResult 中的 week / room_no 拓展为一对一结果
        例如：
            week="(1,3周) , (5-7周)" → [1,3,5,6,7]
            room_no="3B311,3B312" → ["3B311", "3B312"]
        最终生成 week × room_no 的配对组合
        """
        print("开始进行笛卡尔积拓展")
        end_total_results = []

        for result in self.white_room_dict:
            # 1. 拓展周次 → 变成列表
            week_list = parse_weeks(result.week)  # [1,3,5,6,7]

            # 2. 拆分教室 → 变成列表
            room_list = [r.strip() for r in result.room_no.split(',') if r.strip()]

            # 3. 笛卡尔积配对
            for week in week_list:
                for room in room_list:

                    # 如果 room 满足 7号楼A101 格式，则截取后三位数字
                    m = re.match(r'7号楼[ABC](\d{3})$', room)
                    if m:
                        clean_room = m.group(1)  # 取后三位教室号
                    else:
                        clean_room = room  # 羽毛球场等保持原样

                    new_r = ParserResult(
                        building=result.building,
                        floor=result.floor,
                        room_no=clean_room,
                        section=result.section,
                        week=week,
                        weekday=result.weekday
                    )
                    end_total_results.append(new_r)

        # 覆盖最终结果
        self.results = end_total_results
        print(f"拓展结果共计:{len(self.results)}")

    def export_json(self, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in self.results], f, ensure_ascii=False, indent=4)

        print(f"\n🎉 已成功写入 JSON 文件：{output_path}")
        print(f"总记录数: {len(self.results)}")


class GetCourseTable:
    account = None
    password = None
    roomFileName = None
    baseUrl = "http://10.20.208.51/jsxsd"
    session = None
    kbFileName = None
    roomJsonSaveName = None
    tabelJsonSaveName = None
    scheduleJsonSaveName = None

    def __init__(self):
        self.account = WEB_ACCOUNT
        self.password = WEB_PASSWORD
        self.session = requests.session()
        self.cookieStr = None
        self.kbFileName = "kebiao.html"
        self.scheduleJsonSaveName = "total_schedule.json"

    def login(self):
        # TODO: 登录并获取cookies
        account_encoded = base64.b64encode(self.account.encode('utf-8'))
        password_encoded = base64.b64encode(self.password.encode('utf-8'))
        encoded = account_encoded.decode('utf-8') + "%%%" + password_encoded.decode('utf-8')

        # 初始化ddddocr识别验证码
        ocr = ddddocr.DdddOcr(show_ad=False)
        # 获取验证码图片
        captchaResponse = self.session.get(self.baseUrl + "/verifycode.servlet")

        image_bytes = captchaResponse.content

        # 使用ddddocr识别
        captchaResult = ocr.classification(image_bytes)

        data = {
            'loginMethod': "LoginToXk",
            'userAccount': self.account,
            'userPassword': self.password,
            "RANDOMCODE": captchaResult,
            "encoded": encoded
        }

        # 请求登录
        self.session.post(self.baseUrl + "/xk/LoginToXk", data=data)
        # 访问主页
        response = self.session.post(self.baseUrl + "/framework/xsMain.jsp")
        html = etree.HTML(response.text)
        # 校验登录结果
        if "个人中心" in response.text:
            # 成功,保存Cookie记录个人信息
            self.cookieStr = '; '.join([f'{k}={v}' for k, v in self.session.cookies.items()])
            print("登录成功:" + self.cookieStr)
            return True, self.cookieStr
        else:
            # 失败
            msgElem = html.xpath('//*[@id="showMsg"]')  # 定位错误原因
            # print(response.text)
            if msgElem:
                errorMsg = msgElem[0].text.strip()
            else:
                errorMsg = "未知错误，可能为页面结构变化导致未读取到错误信息"
            if "验证码错误" in msgElem or "请先登录系统" == msgElem:
                print("预料之内的异常:", msgElem)
                time.sleep(2)
                return self.login()

            return False, "请尝试重新登陆或检查账号密码是否正确"

    def downloadKb(self):
        # TODO: 下载课表
        # http://10.20.208.51/jsxsd/kbcx/kbxx_kc_ifr
        print("开始下载课表")
        downUrl = self.baseUrl + "/kbcx/kbxx_kc_ifr"
        headers = {
            'referer': 'http://jwn.ccdgut.edu.cn/jsxsd/kbcx/kbxx_xzb',
            'cookie': self.cookieStr,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.52'
        }
        response = self.session.post(url=downUrl, headers=headers)
        content = response.text  # 自动解码成 str
        # 或者 content = response.content.decode('utf-8')

        with open(self.kbFileName, 'w', encoding='utf-8') as fp:
            fp.write(content)