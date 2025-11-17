import base64
import time

import ddddocr

from app.config import WEB_ACCOUNT, WEB_PASSWORD
import requests
from lxml import etree


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


GetSchedule = GetCourseTable()
GetSchedule.login()
GetSchedule.downloadKb()