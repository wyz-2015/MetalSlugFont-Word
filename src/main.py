#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from editor import MainWindow
import version as ver

def main():#程序入口
    print("当前程序版本：{0:s}".format(ver.VERSION))
    app=QApplication([])
    window=MainWindow()
    window.show()
    app.exec()

if(__name__=="__main__"):
    sys.exit(main())
