import csv
import datetime
import hashlib
import json
import time
from urllib import parse
import requests


class MySteelSpider:
    """获取我的钢铁数据"""
    def __init__(self, start_time="", end_time=""):
        """
        默认日期为昨天到今天
        :param start_time:
        :param end_time:
        """
        timeNow = datetime.datetime.now()
        self.now = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        today = timeNow.strftime('%Y-%m-%d')
        yesterday = (timeNow - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        self.yesterday = yesterday
        print(self.yesterday)
        if start_time == "":
            self.startTime = yesterday
        else:
            self.startTime = start_time
        if end_time == "":
            self.endTime = today
        else:
            self.endTime = end_time

    def get_steel_data(self, steel_type):
        """
        :param steel_type: ElectrolyticCopper:电解铜,  Rebar :螺纹钢（HRB400E 20MM，上海市场）
        :return:
        """
        url = "https://index.mysteel.com/zs/newprice/getChartMultiCity.ms?"
        v = str(int(time.time() * 1000))

        path = "path" + "/zs/newprice/getChartMultiCity.ms" + "timestamp" + v + "version1.0.0" + "3BA6477330684B19AA6AF4485497B5F2"
        path = path.encode(encoding='UTF-8')
        sign = hashlib.md5(path).hexdigest().upper()

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68',
            "timestamp": v,
            "X - Requested - With": "XMLHttpRequest",
            "appKey": "47EE3F12CF0C443F8FD51EFDA73AC815",
            "version": "1.0.0",
            "sign": sign
        }
        if steel_type == "ElectrolyticCopper":
            catalog = "%25E7%2594%25B5%25E8%25A7%25A3%25E9%2593%259C_%3A_%25E7%2594%25B5%25E8%25A7%25A3%25E9%2593%259C"
            city = '%25E4%25B8%258A%25E6%25B5%25B7'
            spec = ""
        elif steel_type == "Rebar":
            catalog = "%25E8%259E%25BA%25E7%25BA%25B9%25E9%2592%25A2_%3A_%25E8%259E%25BA%25E7%25BA%25B9%25E9%2592%25A2"
            city = '%25E4%25B8%258A%25E6%25B5%25B7'
            spec = "HRB400E%252020MM_%3A_HRB400E_20MM"
        # "https://index.mysteel.com/zs/newprice/getChartMultiCity.ms?catalog=%25E7%2594%25B5%25E8%25A7%25A3%25E9%2593%259C_%3A_%25E7%2594%25B5%25E8%25A7%25A3%25E9%2593%259C&city=%25E4%25B8%258A%25E6%25B5%25B7&spec=&startTime=2021-08-01&endTime=2021-09-01&callback=json&v=1633001819008"
        v = parse.quote(v)
        url = url + "catalog=" + catalog + "&city=" + city + "&spec=" + spec + "&startTime=" + parse.quote(
            self.startTime) + "&endTime=" + parse.quote(self.endTime) + "&callback=json&v=" + str(v)

        response = requests.get(url=url, headers=header)
        result = response.text
        result = json.loads(result)
        #print(result)
        # print(result["data"][0]["dateValueMap"])
        if len(result["data"]) != 0:
            return result["data"][0]["dateValueMap"]
        else:
            return {}

    def run(self):
        """
        返回两种金属的数据
        :return:
        """
        result = {"ElectrolyticCopper": self.get_steel_data("ElectrolyticCopper"),
                  "Rebar": self.get_steel_data("Rebar")}
        # print(result)
        #{'ElectrolyticCopper': [{'date': '2021-11-01', 'value': '70840'}], 'Rebar': [{'date': '2021-11-01', 'value': '5250'}]}
        try:
            if len(result['ElectrolyticCopper']) >= 1 and len(result['Rebar']) >= 1:
                electrolyticCopper_value = result['ElectrolyticCopper'][0]["value"]
                electrolyticCopper_data = result['ElectrolyticCopper'][0]["date"]
                rebar_value = result['Rebar'][0]["value"]
                rebar_data = result['Rebar'][0]["date"]
            else:
                return "Error"
                # electrolyticCopper_value = result['ElectrolyticCopper'][1]["value"]
                # electrolyticCopper_data = result['ElectrolyticCopper'][1]["date"]
                # rebar_value = result['Rebar'][1]["value"]
                # rebar_data = result['Rebar'][1]["date"]
            Deploy_reader = csv.reader("files/rebar.csv")
            length = len(list(Deploy_reader))
            # 读取内容
            tmp = open("files/rebar.csv", 'r')
            reader = csv.reader(tmp)
            i = 0
            datalist = []
            for item in reader:  # 按行读取
                # 转换utf-8格式\
                datalist.append(item[0])
                i = i + 1
            tmp.close()
            if self.yesterday not in datalist:
                with open("files/rebar.csv", 'a+', newline='')as f:
                    f_csv = csv.writer(f)
                    rows = [[str(rebar_data),str(rebar_value)]]
                    f_csv.writerows(rows)
                with open("files/eleCopper.csv", 'a+', newline='')as f:
                    f_csv = csv.writer(f)
                    rows = [[str(electrolyticCopper_data),str(electrolyticCopper_value)]]
                    f_csv.writerows(rows)
                print(result)
                return result
            else:
                return None
        except:
            return "Error"
