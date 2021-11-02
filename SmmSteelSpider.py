import re
import bs4
from time import sleep
from fake_useragent import UserAgent  # pip install fake_useragent
from selenium import webdriver
import csv
import datetime
import json
import os

import tempfile
import time

temp_file = tempfile.gettempdir()
print(temp_file)


class SmmSteelSpider:
    """获取上海有色数据"""

    def __init__(self, start_time="", end_time="", steel_type=""):
        """
        默认日期为昨天到今天
        :param start_time:
        :param end_time:
        :param steel_type: A00aluminum:A00铝(上海、无锡),  Alumina:氧化铝(山东、河南、山西、广西、贵州),    Electrolytic_manganese:电解锰(湖南)
        """
        self.year = str(datetime.datetime.now().year)+"-"
        self.path = os.path.abspath(os.path.dirname(
            (os.path.dirname(__file__)))) + r"\SteelPriceVis\files"
        timeNow = datetime.datetime.now()
        today = timeNow.strftime('%Y-%m-%d')
        yesterday = (timeNow - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        if start_time == "":
            self.startTime = yesterday
        else:
            self.startTime = start_time
        if end_time == "":
            self.endTime = today
        else:
            self.endTime = end_time
        if steel_type != "":
            self.steel_type = steel_type
        else:
            self.steel_type = ""
        # 定于无界面的Chrome浏览器
        ua = UserAgent()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
        chrome_options.add_argument('--start-maximized')  # 浏览器最大化
        chrome_options.add_argument(
            '--window-size=1920x1080')   # 设置浏览器分辨率（窗口大小）
        chrome_options.add_argument('log-level=3')
        # info(default) = 0# warning = 1# LOG_ERROR = 2# LOG_FATAL = 3
        chrome_options.add_argument('--user-agent=""')  # 设置请求头的User-Agent
        chrome_options.add_argument('--disable-infobars')  # 禁用浏览器正在被自动化程序控制的提示
        chrome_options.add_argument('--incognito')  # 隐身模式（无痕模式）
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('--disable-javascript')  # 禁用javascript
        chrome_options.add_argument(
            '--blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度

        chrome_options.add_argument(
            '--ignore-certificate-errors')  # 禁用扩展插件并实现窗口最大化
        chrome_options.add_argument('–disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        self.driver = webdriver.Chrome(os.path.abspath(
            os.curdir) + r"/chromedriver.exe", chrome_options=chrome_options)

    def __get_steel_data(self, datalist1, datalist2, datalist3):
        """
        :param
        :return:
        """
        driver = self.driver
        driver.get("https://hq.smm.cn/aluminum/fullscreen")
        driver.maximize_window()
        driver.implicitly_wait(8)  # 设置隐式等待，等待时间8秒,隐式等待全局生效
        # 点击账号
        driver.find_element_by_class_name("form-field").click()
        sleep(1)
        # 输入账号
        driver.find_element_by_name("account").send_keys("13215630161")
        # 点击密码
        driver.find_element_by_class_name("login-module-content").click()
        sleep(1)
        # 输入密码
        driver.find_element_by_name("password").send_keys("13215630161dky")
        # 点击登录
        driver.find_element_by_class_name("login-submit-wrap").click()
        # 模拟用户登录完成
        sleep(2)
        html_source = driver.page_source
        # print(html_source)
        f = open(self.path + '\\testclassdata_cn.html',
                 mode="w", encoding="utf-8")
        f.write(html_source)

        soup = bs4.BeautifulSoup(open(self.path + '\\testclassdata_cn.html', encoding='utf-8'),
                                 features='html.parser')  # features值可为lxml
        # print(soup)
        # SMM A00铝
        # SMM氧化铝
        Full_price = soup.find_all('tr')
        # print(jiage)
        file_a = open("files/aluminum.txt", mode="w")
        for data in Full_price:
            print(data.text, file=file_a)
        f1 = open("files/aluminum.txt", "r")
        data = f1.read()
        # 这里要备份一下数据，不然不对
        data1 = data
        # 下面再用正则表达式从str中筛选出我们需要的数据
        # SMM A00铝
        SMMA00 = re.findall("SMM A00铝(.*?)SMM A00铝升贴水", data, re.DOTALL)
        Price_range_SMMA00 = re.findall(r'\d+-\d+', str(SMMA00), re.DOTALL)
        Price_average_SMMA00 = re.findall(r'\d+', str(SMMA00), re.DOTALL)
        Price_time_SMMA00 = re.findall(r'\d\d-\d\d', str(SMMA00), re.DOTALL)
        reg_min = r'(.*?)-'
        reg_max = r'-(.*)'
        reg_ques_max = re.compile(reg_max)
        reg_ques_min = re.compile(reg_min)  # 编译一下正则表达式，运行的更快
        Price_SMMA00range_max = reg_ques_max.findall(
            str(Price_range_SMMA00[0]))
        Price_SMMA00range_min = reg_ques_min.findall(
            str(Price_range_SMMA00[0]))
        # print('SMM A00铝价格区间是', Price_range_SMMA00[0])
        # print('SMM A00铝最大价格是', Price_SMMA00range_max[0])
        # print('SMM A00铝最小价格是', Price_SMMA00range_min[0])
        # print('SMM A00铝均价是', Price_average_SMMA00[2])
        # # 这里应为会搜到2个，所以取最后一个
        # print('时间是', Price_time_SMMA00[1])

        # SMM SMM氧化铝
        SMM = re.findall("SMM氧化铝(.*?)氧化铝\(山东\)", data1, re.DOTALL)
        # print(SMM)
        Price_range_SMM = re.findall(r'\d+-\d+', str(SMM), re.DOTALL)
        Price_average_SMM = re.findall(r'\d+', str(SMM), re.DOTALL)
        Price_time_SMM = re.findall(r'\d\d-\d\d', str(SMM), re.DOTALL)
        Price_SMMrange_max = reg_ques_max.findall(str(Price_range_SMM[0]))
        Price_SMMrange_min = reg_ques_min.findall(str(Price_range_SMM[0]))
        # print('SMM氧化铝价格区间是', Price_range_SMM[0])
        # print('SMM氧化铝最大价格是', Price_SMMrange_max[0])
        # print('SMM氧化铝最小价格是', Price_SMMrange_min[0])
        # print('SMM氧化铝均价是', Price_average_SMM[2])
        # # 这里应为会搜到2个，所以取最后一个
        # print('时间是', Price_time_SMM[1])

        # SMM 电解锰
        # 获取电解锰-湖南
        driver.find_element_by_xpath(
            "/html/body/header/div/div[2]/div/div[2]/div/ul/li[12]/a").click()
        html_source = driver.page_source
        # print(html_source)
        f = open(self.path + '\\testclassdata_cn1.html',
                 mode="w", encoding="utf-8")
        f.write(html_source)

        soup = bs4.BeautifulSoup(open(self.path + '\\testclassdata_cn1.html', encoding='utf-8'),
                                 features='html.parser')  # features值可为lxml
        Full_price = soup.find_all('tr')
        # print(jiage)
        file_a = open("files/Electrolytic_manganese1.txt", mode="w")
        for data in Full_price:
            print(data.text, file=file_a)
        f1 = open("files/Electrolytic_manganese1.txt", "r")
        data = f1.read()
        # 这里要备份一下数据，不然不对
        data1 = data
        Electrolytic_manganese = re.findall(
            "电解锰[(]湖南[)](.*?)电解锰[(]贵州[)]", data1, re.DOTALL)
        Price_range_Electrolytic_manganese = re.findall(r'\d+-\d+', str(Electrolytic_manganese),
                                                        re.DOTALL)
        Price_average_Electrolytic_manganese = re.findall(
            r'\d+', str(Electrolytic_manganese), re.DOTALL)
        Price_time_Electrolytic_manganese = re.findall(
            r'\d\d-\d\d', str(Electrolytic_manganese), re.DOTALL)
        # print(Price_range_Electrolytic_manganese[0])
        Price_ElectrolyticManganese_range_max = reg_ques_max.findall(
            str(Price_range_Electrolytic_manganese[0]))
        Price_ElectrolyticManganese_range_min = reg_ques_min.findall(
            str(Price_range_Electrolytic_manganese[0]))
        # print('电解锰(湖南)价格区间是', Price_range_Electrolytic_manganese[0])
        # print('电解锰(湖南)最大价格是', Price_ElectrolyticManganese_range_max[0])
        # print('电解锰(湖南)最小价格是', Price_ElectrolyticManganese_range_min[0])
        # print('电解锰(湖南)均价是', Price_average_Electrolytic_manganese[2])
        # 这里应为会搜到2个，所以取最后一个
        #print('时间是', Price_time_Electrolytic_manganese[1])
        driver.quit()
        self.now1 = self.year + Price_time_SMMA00[1].replace("/", "-")
        self.now2 = self.year + Price_time_SMM[1].replace("/", "-")
        self.now3 = self.year + \
            Price_time_Electrolytic_manganese[1].replace("/", "-")

        op1 = False
        op2 = False
        op3 = False
        if self.now1 not in datalist1:
            op1 = True

        if self.now2 not in datalist2:
            op2 = True

        if self.now2 not in datalist3:
            op3 = True

        A00aluminum_result = {
            "msg": "steel_type值错误，请传入‘A00aluminum’或‘Alumina’或‘Electrolytic_manganese’！"
        }
        Alumina_result = {
            "msg": "steel_type值错误，请传入‘A00aluminum’或‘Alumina’或‘Electrolytic_manganese’！"
        }
        ElectrolyticManganese_result = {
            "msg": "steel_type值错误，请传入‘A00aluminum’或‘Alumina’或‘Electrolytic_manganese’！"
        }

        A00aluminum_result = {
            "name": u"SMM A00铝",
            "city": u"上海、无锡",
            "priceMax": Price_SMMA00range_max[0],
            "priceMin": Price_SMMA00range_min[0],
            "priceAverage": Price_average_SMMA00[2],
            "time": Price_time_SMMA00[1]
        }
        Alumina_result = {
            "name": u"SMM氧化铝",
            "city": u"山东、河南、山西、广西、贵州",
            "priceMax": Price_SMMrange_max[0],
            "priceMin": Price_SMMrange_min[0],
            "priceAverage": Price_average_SMM[2],
            "time": Price_time_SMM[1]
        }
        ElectrolyticManganese_result = {
            "name": u"电解锰",
            "city": u"湖南",
            "priceMax": Price_ElectrolyticManganese_range_max[0],
            "priceMin": Price_ElectrolyticManganese_range_min[0],
            "priceAverage": Price_average_Electrolytic_manganese[2],
            "time": Price_time_Electrolytic_manganese[1]
        }

        if op1 == True:
            with open("files/SMMA00.csv", 'a+', newline='')as f:
                f_csv = csv.writer(f)
                rows = [[str(self.year+Price_time_SMMA00[1]), str(Price_average_SMMA00[2]),
                         str(Price_SMMA00range_min[0]), str(Price_SMMA00range_max[0])]]
                f_csv.writerows(rows)

        if op2 == True:
            with open("files/SMMalumina.csv", 'a+', newline='')as f:
                f_csv = csv.writer(f)
                rows = [[str(self.year+Price_time_SMM[1]), str(Price_average_SMM[2]),
                         str(Price_SMMrange_min[0]), str(Price_SMMrange_max[0])]]
                f_csv.writerows(rows)

        if op3 == True:
            with open("files/eleManganese.csv", 'a+', newline='')as f:
                f_csv = csv.writer(f)
                rows = [[str(self.year+Price_time_Electrolytic_manganese[1]),
                         str(Price_average_Electrolytic_manganese[2])]]
                f_csv.writerows(rows)

        if op1 == False or op2 == False or op3 == False:
            return None

        return json.dumps(A00aluminum_result), json.dumps(Alumina_result), json.dumps(ElectrolyticManganese_result)

    def run(self):
        """
        返回两种金属的数据
        :return:
        """
        op1 = False
        op2 = False
        op3 = False
        Deploy_reader = csv.reader("files/SMMA00.csv")
        length = len(list(Deploy_reader))
        # 读取内容
        tmp = open("files/SMMA00.csv", 'r')
        reader = csv.reader(tmp)
        i = 0
        datalist1 = []
        for item in reader:  # 按行读取
            # 转换utf-8格式
            datalist1.append(item[0])
            i = i + 1
        tmp.close()

        Deploy_reader = csv.reader("files/SMMalumina.csv")
        length = len(list(Deploy_reader))
        # 读取内容
        tmp = open("files/SMMalumina.csv", 'r')
        reader = csv.reader(tmp)
        i = 0
        datalist2 = []
        for item in reader:  # 按行读取
            # 转换utf-8格式
            datalist2.append(item[0])
            i = i + 1
        tmp.close()

        Deploy_reader = csv.reader("files/eleManganese.csv")
        length = len(list(Deploy_reader))
        # 读取内容
        tmp = open("files/eleManganese.csv", 'r')
        reader = csv.reader(tmp)
        i = 0
        datalist3 = []
        for item in reader:  # 按行读取
            # 转换utf-8格式
            datalist3.append(item[0])
            i = i + 1
        tmp.close()

        try:
            tempresult = self.__get_steel_data(datalist1, datalist2, datalist3)
            if tempresult != None:
                result = [tempresult[0], tempresult[1], tempresult[2]]
                print(result)
                return result
            else:
                return tempresult
        except:
            return "Error"
