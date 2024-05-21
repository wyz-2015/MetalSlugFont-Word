#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from editor import MainWindow

def main():#程序入口
    app=QApplication([])
    window=MainWindow()
    window.show()
    app.exec()

if(__name__=="__main__"):
    sys.exit(main())
