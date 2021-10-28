# -*-coding:utf-8-*-
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
from PyQt5.QtWidgets import *
from QtWindow import Ui_MainWindow
from fileProcessing import FileProcessing
from PyQt5 import QtCore, QtGui, QtWidgets
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from pricePredict import PricePredict
import os
from matplotlib.font_manager import FontProperties

# 创建一个matplotlib图形绘制类
class MyFigure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        # 第一步：创建一个创建Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # 第二步：在父类中激活Figure窗口
        super(MyFigure, self).__init__(self.fig)  # 此句必不可少，否则不能显示图形

    # 重写clear方法
    # def clear(self):
    #     self.fig.clf()


class MainDialogImgBW(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainDialogImgBW, self).__init__()
        self.setupUi(self)
        # self.setWindowTitle("显示matplotlib绘制图形")
        # self.setMinimumSize(0, 0)

        # 在GUI的groupBox中创建一个布局，用于添加MyFigure类的实例（即图形）后其他部件。
        self.gridlayout = QGridLayout(self.groupBox)  # 继承容器groupBox

        # 读取缓存数据
        self.file_name = ["alumina", "SMMA00", "rebar", "silicomanganese", "eleManganese",  "thermalCoal", "eleCopper",
                          "SMMalumina"]
        self.fp = FileProcessing()
        self.data_set = []
        for each in self.file_name:
            data = self.fp.load_data("files/" + each, 'csv')
            self.data_set.append(data)
        self.table_data = self.fp.load_data("dataSet")
        # 保存当前页面状态
        self.now_page = "main"
        # 当前选择的时间尺度,默认为天
        self.time_scale = "day"
        # 坐标轴稀疏尺度，根据日期尺度变化
        self.tick_spacing = 20
        self.price_predictor = PricePredict()
        # 换乘系统设置
        self.setting = self.fp.load_data("setting")
        # 开启定时更新后屏蔽按钮
        if self.setting["open_regular_update"] == "true":
            self.regular_update.setEnabled(False)
            #####################################################
            # 开启定时更新后台任务
            #####################################################
            hours = int(self.setting["update_time"].split(":")[0])
            mins = int(self.setting["update_time"].split(":")[1])
            print(hours, mins)
            scheduler = BackgroundScheduler()
            scheduler.add_job(self.clickUpdate, 'cron', day_of_week='0-6', hour=hours, minute=mins)
            scheduler.start()

        #####################################################################
        # 绑定按钮点击事件
        #####################################################################
        self.is_first_draw = True
        self.mainPageButton.clicked.connect(self.drawAllTable)
        self.rebarButton.clicked.connect(lambda: self.drawSingleTable("rebar"))
        self.eleCopperButton.clicked.connect(lambda: self.drawSingleTable("eleCopper"))
        self.aluminaButton.clicked.connect(lambda: self.drawSingleTable("alumina"))
        self.silicomanganeseButton.clicked.connect(lambda: self.drawSingleTable("silicomanganese"))
        self.thermalCoalButton.clicked.connect(lambda: self.drawSingleTable("thermalCoal"))
        self.SMMA00Button.clicked.connect(lambda: self.drawSingleTable("SMMA00"))
        self.SMMaluminaButton.clicked.connect(lambda: self.drawSingleTable("SMMalumina"))
        self.eleManganeseButton.clicked.connect(lambda: self.drawSingleTable("eleManganese"))
        self.dayButton.clicked.connect(lambda: self.redrawByDate("day"))
        self.weekButton.clicked.connect(lambda: self.redrawByDate("week"))
        self.monthButton.clicked.connect(lambda: self.redrawByDate("month"))
        self.yearButton.clicked.connect(lambda: self.redrawByDate("year"))

        self.regular_update.clicked.connect(lambda: self.openRegularUpdate())
        self.click_update.clicked.connect(lambda: self.clickUpdate())
        self.insert_report.clicked.connect(lambda: self.insertReport())
        self.predict.clicked.connect(lambda: self.pricePredict())
        self.drawAllTable()

        pass

    def overview(self):
        """
        同时显示8种金属的概览图
        """
        print("overview")
        self.F = MyFigure(width=3, height=3, dpi=100)

        # F1.fig.suptitle("Figuer_4")
        # 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法
        data = []
        for each in self.file_name:
            data.append(self.regenerateDataByTime(each))

        index = 331
        for i in range(0, len(data)):
            self.F.axes = self.F.fig.add_subplot(index)
            index += 1
            # x轴稀疏处理
            self.F.axes.plot(data[i]["date"], data[i]["value"], "r", linewidth=0.5)
            self.F.axes.set_title(self.table_data[self.file_name[i]]["name"]+" 走势图", fontsize=10, fontweight='bold', fontproperties="SimHei")
            if self.tick_spacing != -1:
                self.F.axes.xaxis.set_major_locator(ticker.MultipleLocator(self.tick_spacing))

            # 旋转x标签
            for tick in self.F.axes.get_xticklabels():
                tick.set_rotation(90)
            for size in self.F.axes.get_xticklabels():  # 获取x轴上所有坐标，并设置字号
                size.set_fontname('Times New Roman')
                size.set_fontsize('8')
            for size in self.F.axes.get_yticklabels():  # 获取y轴上所有坐标，并设置字号
                # size.set_fontname(' Microsoft YaHei')  # 雅黑
                size.set_fontsize('8')

        self.F.fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.3,
                                   hspace=0.8)  # wspace 子图横向间距， hspace 代表子图间的纵向距离，left 代表位于图像不同位置

        self.gridlayout.addWidget(self.F, 0, 0)  # row, column
        # self.update()

    def drawSingleChart(self, chart_type, is_export=False):
        """
        绘制单个折线图
        :param chart_type: 绘图的金属种类
        :param is_export:
        :return:
        """

        data = self.regenerateDataByTime(chart_type)
        print("chart", chart_type)
        self.F = MyFigure(width=3, height=3, dpi=100)
        self.F.axes = self.F.fig.add_subplot(111)
        # x轴稀疏处理
        index = self.file_name.index(chart_type)
        myfont = FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
        self.F.axes.plot(data["date"], data["value"], "r", linewidth=0.5, label=self.table_data[chart_type]["label"])
        self.F.axes.set_title(self.table_data[chart_type]["name"]+" 走势图", fontsize=15, fontweight='bold', fontproperties="SimHei")
        self.F.axes.legend(loc='upper right', prop=myfont, framealpha=0.4)
        if self.tick_spacing != -1:
            self.F.axes.xaxis.set_major_locator(ticker.MultipleLocator(self.tick_spacing))
        # 旋转x标签
        for tick in self.F.axes.get_xticklabels():
            tick.set_rotation(30)
        for size in self.F.axes.get_xticklabels():  # 获取x轴上所有坐标，并设置字号
            size.set_fontname('Times New Roman')
            size.set_fontsize('8')
        for size in self.F.axes.get_yticklabels():  # 获取y轴上所有坐标，并设置字号
            # size.set_fontname(' Microsoft YaHei')  # 雅黑
            size.set_fontsize('8')
        self.F.axes.grid()
        if not is_export:
            self.gridlayout.addWidget(self.F, 0, 0)
        else:
            self.F.fig.set_size_inches(10, 7)
            self.F.fig.savefig("./files/imgs/"+chart_type, dpi=800)
        pass

    def drawAllTable(self):
        """
        显示八种金属价格表
        :param MainWindow:
        :return:
        """
        if self.is_first_draw:
            self.is_first_draw = False
        else:
            self.tableWidget.deleteLater()
        self.now_page = "main"
        print("main!!")

        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(290, 140, 902, 118))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(9)
        self.tableWidget.setRowCount(3)

        self.setTableContent(self.tableWidget)
        # self.layout.addWidget(self.tableWidget)

        header_list = ["产品"]
        for each in self.table_data:
            header_list.append(self.table_data[each]["name"])
        self.tableWidget.setHorizontalHeaderLabels(header_list)

        index = 1
        for each in self.table_data:
            price_item = QtWidgets.QTableWidgetItem(self.table_data[each]["price"])
            com_week_text = self.table_data[each]["com_week"]
            com_year_text = self.table_data[each]["com_year"]

            com_week_text = self.repalceStrUpDown(com_week_text)
            com_year_text = self.repalceStrUpDown(com_year_text)

            com_week_item = QtWidgets.QTableWidgetItem(com_week_text)
            com_year_item = QtWidgets.QTableWidgetItem(com_year_text)
            self.tableWidget.setItem(0, index, price_item)
            self.tableWidget.setItem(1, index, com_week_item)
            self.tableWidget.setItem(2, index, com_year_item)
            index += 1

        self.tableWidget.show()
        #######################################################################
        self.overview()
        pass

    def repalceStrUpDown(self, strs):
        """字符串中的+-替换成中文"""
        if "+" in strs:
            strs = strs.replace('+', "涨 ")
        elif "-" in strs:
            strs = strs.replace("-", "跌 ")
        return strs

    def drawSingleTable(self, steel_type):
        """显示单个金属的表格"""
        print(steel_type)
        self.now_page = steel_type
        self.tableWidget.deleteLater()
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(630, 140, 202, 118))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(3)
        self.setTableContent(self.tableWidget)

        header_list = ["产品", self.table_data[steel_type]["name"]]
        self.tableWidget.setHorizontalHeaderLabels(header_list)

        price_item = QtWidgets.QTableWidgetItem(self.table_data[steel_type]["price"])
        com_week_text = self.table_data[steel_type]["com_week"]
        com_year_text = self.table_data[steel_type]["com_year"]
        com_week_text = self.repalceStrUpDown(com_week_text)
        com_year_text = self.repalceStrUpDown(com_year_text)
        com_week_item = QtWidgets.QTableWidgetItem(com_week_text)
        com_year_item = QtWidgets.QTableWidgetItem(com_year_text)
        self.tableWidget.setItem(0, 1, price_item)
        self.tableWidget.setItem(1, 1, com_week_item)
        self.tableWidget.setItem(2, 1, com_year_item)

        self.tableWidget.show()
        self.drawSingleChart(steel_type)
        pass

    def setTableContent(self, table_widget):
        """设置表格样式"""
        table_widget.setStyleSheet("background-color: rgb(240, 240, 240);")
        table_widget.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:rgb(240, 240, 240);}")
        table_widget.verticalHeader().setVisible(False)
        table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        header_item1 = QtWidgets.QTableWidgetItem("本周价格(元/吨)")
        header_item2 = QtWidgets.QTableWidgetItem("环比上周(元/吨)")
        header_item3 = QtWidgets.QTableWidgetItem("同比去年(元/吨)")
        table_widget.setItem(0, 0, header_item1)
        table_widget.setItem(1, 0, header_item2)
        table_widget.setItem(2, 0, header_item3)
        pass

    def redrawByDate(self, time_range):
        """
        根据选择的年月日切换数据，重绘
        :param time_range:
        :return:
        """
        print(time_range)
        self.time_scale = time_range
        if time_range == "day":
            self.tick_spacing = 20
        elif time_range == "week":
            self.tick_spacing = 4
        elif time_range == "month":
            self.tick_spacing = 1
        elif time_range == "year":
            self.tick_spacing = -1

        if self.now_page == "main":
            self.overview()
        else:
            self.drawSingleChart(self.now_page)
        pass

    def regenerateDataByTime(self, steel_type):
        """
        根据选择的时间尺度计返回数据，默认为日
        :param steel_type:
        :return: 新时间尺度的数据
        """
        print("regenerateDataByTime", steel_type)
        time_range = self.time_scale
        index = self.file_name.index(steel_type)
        data = self.data_set[index]
        result = {}
        if time_range == "day":
            result = data

        elif time_range == "week":
            result["date"] = []
            result["value"] = []
            day_count = 0
            value_count = 0
            for index in range(len(data["date"])):
                week = self.getWeekDay(data["date"][index])
                if week == 1 and day_count != 0:
                    result["date"].append(data["date"][index])
                    result["value"].append(int(value_count / day_count))
                    day_count = 0
                    value_count = 0
                if week == 1 and day_count == 0:
                    result["date"].append(data["date"][index])
                    result["value"].append(data["value"][index])

                day_count += 1
                value_count += data["value"][index]
                if week != 1 and index == (len(data["date"]) - 1):
                    result["date"].append(data["date"][index])
                    result["value"].append(int(value_count / day_count))

        elif time_range == "month":
            result["date"] = []
            result["value"] = []
            day_count = 0
            value_count = 0
            for index in range(len(data["date"])):
                now_day = data["date"][index].split("-")[2]
                if (now_day == "1" or now_day == "01") and day_count != 0:
                    result["date"].append(data["date"][index])
                    result["value"].append(int(value_count / day_count))
                    day_count = 0
                    value_count = 0
                if (now_day == "1" or now_day == "01") and day_count == 0:
                    result["date"].append(data["date"][index])
                    result["value"].append(data["value"][index])

                day_count += 1
                value_count += data["value"][index]
                if index == (len(data["date"]) - 1) and day_count != 0:
                    result["date"].append(data["date"][index])
                    result["value"].append(int(value_count / day_count))

        elif time_range == "year":
            result["date"] = []
            result["value"] = []
            day_count = 0
            value_count = 0
            for index in range(len(data["date"]) - 1):
                now_year = data["date"][index].split("-")[0]
                next_year = data["date"][index + 1].split("-")[0]
                if next_year != now_year and day_count != 0:
                    result["date"].append(data["date"][index + 1])
                    result["value"].append(int(value_count / day_count))
                    day_count = 0
                    value_count = 0
                if next_year != now_year and day_count == 0:
                    result["date"].append(data["date"][index])
                    result["value"].append(data["value"][index])
                day_count += 1
                value_count += data["value"][index]
                if index == (len(data["date"]) - 2) and day_count != 0:
                    result["date"].append(data["date"][index + 1])
                    result["value"].append(int(value_count / day_count))
                elif index == (len(data["date"]) - 2) and day_count == 0:
                    result["date"].append(data["date"][index + 1])
                    result["value"].append(data["value"][index + 1])
        return result

    def getWeekDay(self, date):
        """通过日期计算星期几"""
        date = datetime.strptime(date, "%Y-%m-%d")
        week = date.weekday() + 1
        return week

    def openRegularUpdate(self):
        """
        开启定时更新功能
        :return:
        """
        self.setting["open_regular_update"] = "true"
        self.fp.save_file(self.setting, "setting")
        self.regular_update.setEnabled(False)
        self.windowMessage("提示", "定时更新开启成功，更新时间为每天：" + self.setting["update_time"])
        pass

    def clickUpdate(self):
        """点击更新功能"""


        pass

    def windowMessage(self, title, message):
        """弹窗提示信息"""
        QMessageBox.information(self, title, message, QMessageBox.Yes)
        pass

    def pricePredict(self):
        """预测功能"""
        # self.file_name = ["rebar", "eleCopper", "alumina", "silicomanganese", "thermalCoal", "SMMA00", "SMMalumina",
        #                   "eleManganese"]
        need_train = False
        now_time = datetime.now()
        last_time = datetime.strptime(self.setting["last_training"], "%Y-%m-%d")
        # 每七天需要重新训练一次
        if (now_time - last_time).days > 7:
            self.windowMessage("提示", "预测模型需要重新训练，耗时较长，请耐心等待，点击确认开始")
            need_train = True
            self.setting["last_training"] = datetime.now().strftime('%Y-%m-%d')
            self.fp.save_file(self.setting, "setting")
        else:
            self.windowMessage("提示", "点击确认开始预测计算，请耐心等待")
        if self.now_page == "main":
            res = []
            for i in range(len(self.file_name)):
                res.append(self.price_predictor.predictPrice(self.data_set[i]["value"], self.file_name[i], need_train))
            messages = ""
            for i in range(len(self.file_name)):
                messages += self.table_data[self.file_name[i]]["name"] + " : " + str(res[i])
                if i != (len(self.file_name) - 1):
                    messages += " , "
        else:
            res = self.price_predictor.predictPrice(self.data_set[self.file_name.index(self.now_page)]["value"], self.now_page, need_train)
            messages = self.table_data[self.now_page]["name"] + " : " + str(res)

        self.windowMessage("下一天预测结果", messages)
        pass

    def insertReport(self):
        """插入报告功能"""
        if not os.path.exists("files/imgs"):
            os.makedirs(os.getcwd()+"\\files\\imgs")

        # self.F.fig.savefig("./files/imgs/test", dpi=600)
        self.windowMessage("提示", "点击确认开始导出报告，请耐心等待")
        for i in self.file_name:
            self.drawSingleChart(i,True)
        self.windowMessage("提示", "导出成功！")
        pass

