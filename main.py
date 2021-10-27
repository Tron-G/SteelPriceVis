# -*-coding:utf-8-*-
import sys
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5

from drawLine import *

if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # mainW = QMainWindow()
    #
    # ui = QtWindow.Ui_MainWindow()
    # ui.setupUi(mainW)
    #
    # mainW.show()
    #
    # sys.exit(app.exec_())

    app = QApplication(sys.argv)
    line = MainDialogImgBW()
    line.show()
    sys.exit(app.exec_())

