from time import sleep, ctime
import re
import bs4
import os
from time import sleep
from fake_useragent import UserAgent  # pip install fake_useragent
from selenium import webdriver
import csv
import datetime
import json
import time
import tempfile
temp_file = tempfile.gettempdir()


class ZczxSteelSSpider:
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
        chrome_options.add_argument('--start-maximized')  # 浏览器最大化
        chrome_options.add_argument(
            '--window-size=1920x1080')  # 设置浏览器分辨率（窗口大小）

        chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
        chrome_options.add_argument('log-level=3')
        # info(default) = 0# warning = 1# LOG_ERROR = 2# LOG_FATAL = 3
        chrome_options.add_argument('--disable-infobars')  # 禁用浏览器正在被自动化程序控制的提示
        chrome_options.add_argument('--incognito')  # 隐身模式（无痕模式）
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('--disable-javascript')  # 禁用javascript
        chrome_options.add_argument(
            '--blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        #
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
        #driver = webdriver.Chrome(os.path.abspath(os.curdir) + r"/chromedriver.exe")
        url1 = "https://my.sci99.com/sso/login.aspx?backurl=https%3a%2f%2fprices.sci99.com%2fcn%2fsearch.aspx%3fkeyword%3d%25e6%25b0%25a7%25e5%258c%2596%25e9%2593%259d%26token%3defcb96097305d406%26requestid%3d39b7e56afa35842&RequestId=bdc3c98e3096169f"
        driver.get(url1)
        driver.maximize_window()
        driver.implicitly_wait(8)  # 设置隐式等待，等待时间8秒,隐式等待全局生效
        # 点击登录
        sleep(1)
        driver.find_element_by_name("SciName").click()
        # 输入账号
        driver.find_element_by_name("SciName").send_keys("gxdky_dsm")
        sleep(2)
        # 点击密码
        driver.find_element_by_name("SciPwd").click()
        # 输入密码
        driver.find_element_by_name("SciPwd").send_keys("778899")
        # 点击登录
        sleep(1)
        # 登录
        driver.find_element_by_class_name("btnwrap").click()
        sleep(1)
        # 刷新一次
        driver.refresh()
        sleep(3)
        # 点击氧化铝
        driver.find_element_by_xpath(
            '//*[@id="form1"]/div[5]/div[2]/div[2]/dl[1]/dd/a[1]').click()
        time.sleep(3)
        # 点击一级
        driver.find_element_by_xpath('//*[@id="dtModel"]/a[4]').click()
        time.sleep(3)
        # 当前网页的源代码
        html_source1 = driver.page_source
        # 搜索硅锰（6517）
        sleep(1)
        driver.switch_to.frame("headerlogin")
        sleep(1)
        driver.find_element_by_class_name("input_search").send_keys("硅锰（6517）")
        driver.find_element_by_xpath(
            '//span[@data-bind="click: search"]').click()
        sleep(5)
        html_source2 = driver.page_source

        # 搜索动力煤（Q5500）
        sleep(2)
        driver.switch_to.frame("headerlogin")
        sleep(1)
        driver.find_element_by_class_name(
            "input_search").send_keys("动力煤（Q5500）")
        driver.find_element_by_xpath(
            '//span[@data-bind="click: search"]').click()
        sleep(5)
        html_source3 = driver.page_source
        ff1 = open(self.path + './zczx_data_AL0.html',
                   mode="w", encoding="utf-8")
        ff1.write(html_source1)
        ff2 = open(self.path + './zczx_data_6157.html',
                   mode="w", encoding="utf-8")
        ff2.write(html_source2)
        ff3 = open(self.path + './zczx_data_Q5500.html',
                   mode="w", encoding="utf-8")
        ff3.write(html_source3)
        ############
        # 统计数据
        # 氧化铝

        soup1 = bs4.BeautifulSoup(open(self.path + '/zczx_data_AL0.html', encoding='utf-8'),
                                  features='html.parser')  # feature
        Full_price1 = soup1.find_all('tr')
        with open(self.path + '/zczx_data.txt', 'w') as f:
            for data in Full_price1:
                print(data.text, file=f)
        f1 = open(self.path + '/zczx_data.txt', "r")
        data1 = f1.read()
        # 这里要备份一下数据，不然不对
        # print(data1)
        ALO = re.findall("氧化铝\\n一级\\n\\n贵州(.*?)点击查看更多", data1, re.DOTALL)
        # print(ALO)
        Price1 = re.findall(r'\d+', str(ALO), re.DOTALL)
        time1 = re.findall(r'\d\d/\d\d\\n', str(ALO), re.DOTALL)

        # print('氧化铝最低价是', Price1[0])
        # print('氧化铝最高价是', Price1[1])
        # print('氧化铝最均价是', Price1[2])
        # print('日期是', time1[0])
        sleep(1)
        # 动力煤
        soup2 = bs4.BeautifulSoup(open(self.path + '/zczx_data_6157.html', encoding='utf-8'),
                                  features='html.parser')  # features值可为lxml

        Full_price2 = soup2.find_all('tr')

        with open(self.path + '/zczx_data2.txt', 'w') as g:
            for data in Full_price2:
                print(data.text, file=g)
        f2 = open(self.path + '/zczx_data2.txt', "r")
        data2 = f2.read()
        guimeng6157 = re.findall(
            "硅锰\\n6517\\n\\n贵州(.*?)点击查看更多", data2, re.DOTALL)
        # print(guimeng6157)
        Price22 = re.findall(r'\d+', str(guimeng6157), re.DOTALL)
        time22 = re.findall(r'\d\d/\d\d\\n', str(guimeng6157), re.DOTALL)
        # print('硅锰（6517）最低价是', Price22[0])
        # print('硅锰（6517）最高价是', Price22[1])
        # print('硅锰（6517）最均价是', Price22[2])
        # print('日期是', time22[0])

        # 动力煤
        soup3 = bs4.BeautifulSoup(open(self.path + '/zczx_data_Q5500.html', encoding='utf-8'),
                                  features='html.parser')  # features值可为lxml
        # print(soup)
        # SMM A00铝
        # SMM氧化铝
        Full_price3 = soup3.find_all('tr')
        with open(self.path + '/zczx_data3.txt', 'w') as hk:
            for data in Full_price3:
                print(data.text, file=hk)
        f3 = open(self.path + '/zczx_data3.txt', "r")
        data3 = f3.read()
        dongQ5500 = re.findall(
            "动力煤\\nQ5500\\n\\n山西(.*?)点击查看更多", data3, re.DOTALL)
        # print("dongQ5500")
        # print(dongQ5500)
        Price33 = re.findall(r'\d+', str(dongQ5500), re.DOTALL)
        time33 = re.findall(r'\d\d/\d\d\\n', str(dongQ5500), re.DOTALL)

        # print('动力煤（Q5500）最低价是', Price33[0])
        # print('动力煤（Q5500）最高价是', Price33[1])
        # print('动力煤（Q5500）最均价是', Price33[2])
        # print('日期是', time33[0])
        driver.quit()
        self.now1 = self.year + time22[0].replace("/", "-").replace(r"\n", "")
        self.now2 = self.year + time1[0].replace("/", "-").replace(r"\n", "")
        self.now3 = self.year + time33[0].replace("/", "-").replace(r"\n", "")

        op1 = False
        op2 = False
        op3 = False
        if self.now1 not in datalist1:
            op1 = True

        if self.now2 not in datalist2:
            op2 = True

        if self.now3 not in datalist3:
            op3 = True
        print(self.now1, self.now2, self.now3)
        print(op1, op2, op3)
        Alumina_result = {
            "name": u"氧化铝",
            "city": u"贵州",
            "priceMax": Price1[1],
            "priceMin": Price1[0],
            "priceAverage": Price1[2],
            "time": time22[0]
        }
        SiliconManganese_result = {
            "name": u"硅锰（6517）",
            "city": u"贵州",
            "priceMax": Price22[1],
            "priceMin": Price22[0],
            "priceAverage": Price22[2],
            "time": time1[0]
        }
        SteamCoal_result = {
            "name": u"动力煤（Q5500）",
            "city": u"山西",
            "priceMax": Price33[1],
            "priceMin": Price33[0],
            "priceAverage": Price33[2],
            "time": time33[0]
        }

        if op1 == True:
            with open("files/alumina.csv", 'a+', newline='')as f:
                f_csv = csv.writer(f)
                temp = time22[0].replace('/', '-')
                temp0 = temp.replace(r'\n', '')
                rows = [[str(self.year+temp0), str(Price1[2])]]
                f_csv.writerows(rows)

        if op2 == True:
            with open("files/silicomanganese.csv", 'a+', newline='')as f:
                f_csv = csv.writer(f)
                temp = time1[0].replace('/', '-')
                temp0 = temp.replace(r'\n', '')
                rows = [[str(self.year+temp0), str(Price22[2])]]
                f_csv.writerows(rows)

        if op3 == True:
            with open("files/thermalCoal.csv", 'a+', newline='')as f:
                f_csv = csv.writer(f)
                temp = time33[0].replace('/', '-')
                temp0 = temp.replace(r'\n', '')
                rows = [[str(self.year+temp0), str(Price33[2])]]
                f_csv.writerows(rows)

        if op1 == False or op2 == False or op3 == False:
            return None

        return json.dumps(Alumina_result), json.dumps(SiliconManganese_result), json.dumps(SteamCoal_result)

    def run(self):
        """
        返回两种金属的数据
        :return:
        """
        # 读取csv 如果当前日期在第一列中，则不进行爬虫

        # 获取行数
        Deploy_reader = csv.reader("files/alumina.csv")
        length = len(list(Deploy_reader))
        # 读取内容
        tmp = open("files/alumina.csv", 'r')
        reader = csv.reader(tmp)
        i = 0
        datalist1 = []
        for item in reader:  # 按行读取
            # 转换utf-8格式
            datalist1.append(item[0])
            i = i + 1
        tmp.close()

        # 获取行数
        Deploy_reader = csv.reader("files/silicomanganese.csv")
        length = len(list(Deploy_reader))
        # 读取内容
        tmp = open("files/silicomanganese.csv", 'r')
        reader = csv.reader(tmp)
        i = 0
        datalist2 = []
        for item in reader:  # 按行读取
            # 转换utf-8格式
            datalist2.append(item[0])
            i = i + 1
        tmp.close()

        # 获取行数
        Deploy_reader = csv.reader("files/thermalCoal.csv")
        length = len(list(Deploy_reader))
        # 读取内容
        tmp = open("files/thermalCoal.csv", 'r')
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
