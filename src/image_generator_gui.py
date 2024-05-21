from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from src_parser import htm2list
from checker import full_check2
from image_generator import img_generate
import sys
from pathlib import Path

class Img_gen_gui(QWidget):#图像生成器GUI前端类
    def __init__(self):
        super(Img_gen_gui,self).__init__()
        self.setWindowTitle("图像生成器")
        icon=Path.cwd() / "static" / "assets" / "fonts" / "font-1" / "ms-blue" / "letters" / "lower-case" / "g.png"
        #print(icon)
        self.setWindowIcon(QIcon(str(icon)))
        self.current_src=None

        (self.ls,self.pm,self.el)=tuple(None for i in range(3))

        #(self.lb1,self.lb2,self.lb3)=tuple(QLabel() for i in range(3))
        #layout_lbs0=QHBoxLayout()
        #layout_lbs0.addWidget(self.lb1)
        #layout_lbs0.addWidget(QSplitter())
        #layout_lbs0.addWidget(self.lb2)
        #layout_lbs0.addWidget(QSplitter())
        #layout_lbs0.addWidget(self.lb3)

        #### 进度条 ####
        self.proc_bar=QProgressBar()
        self.proc_bar.setRange(0,3)
        self.proc_bar.setTextVisible(False)
        self.lb_proc=QLabel()
        layout_proc=QHBoxLayout()
        for i in (self.proc_bar,self.lb_proc):
            layout_proc.addWidget(i)

        #### 调参数的 ####
        self.lb_ls=QLabel("行距：")
        self.qsb_ls=QSpinBox()
        #self.qsb_ls.setMinimum(0)
        self.qsb_ls.setRange(0,1000)
        layout_ls=QHBoxLayout()
        for i in (self.lb_ls,self.qsb_ls):
            layout_ls.addWidget(i)
#
        self.lbs_pm=[QLabel(text) for text in ("页边距(左右x,上下y)：(",",",")")]
        (self.qsb_pm_x,self.qsb_pm_y)=tuple(QSpinBox() for i in range(2))
        for qsb in (self.qsb_pm_x,self.qsb_pm_y):
            #qsb.setMinimum(0)
            qsb.setRange(0,1000)
        layout_pm=QHBoxLayout()
        for i in (self.lbs_pm[0],self.qsb_pm_x,self.lbs_pm[1],self.qsb_pm_y,self.lbs_pm[2]):
            layout_pm.addWidget(i)

        self.lb_el=QLabel("空行行高：")
        self.qsb_el=QSpinBox()
        #self.qsb_el.setMinimum(0)
        self.qsb_el.setRange(0,1000)
        layout_el=QHBoxLayout()
        for i in (self.lb_el,self.qsb_el):
            layout_el.addWidget(i)

        #### 按钮 ####
        self.btn_default=QPushButton("恢复默认参数")

        (self.btn_make,self.btn_view,self.btn_save,self.btn_exit,)=(QPushButton("生成"),QPushButton("预览"),QPushButton("保存"),QPushButton("退出"),)
        layout_btns=QHBoxLayout()
        for i in (self.btn_make,self.btn_view,self.btn_save,self.btn_exit,):
            layout_btns.addWidget(i)

        self.message_browser=QTextBrowser()

        layout_main=QVBoxLayout()
        for i in (layout_proc,layout_ls,layout_pm,layout_el):#,self.message_browser):
            layout_main.addLayout(i)
        layout_main.addWidget(self.btn_default)
        layout_main.addLayout(layout_btns)
        layout_main.addWidget(self.message_browser)
        self.setLayout(layout_main)

        for i in (self.btn_exit,self.btn_make,self.btn_save,self.btn_view,self.btn_default):
            i.clicked.connect(self.btns_center)
        for i in (self.qsb_el,self.qsb_ls,self.qsb_pm_x,self.qsb_pm_y):
            i.valueChanged.connect(self.func_qsb_chenged)

        #### 初始化一些部件 ####
        self.proc_reset()
        self.btns_reset()
        self.current_gen_img=None

        self.func_default()

    def proc_reset(self):#进度条复位
        self.lb_proc.setText("就绪")
        self.proc_bar.setValue(0)
    
    def btns_reset(self):#按钮复位
        for i in (self.btn_save,self.btn_view):
            i.setEnabled(False)

    def btns_center(self):#按钮信号处理中心
        #print(self.sender())
        match self.sender():
            case self.btn_exit:
                self.close()
            case self.btn_make:
                self.func_make()
            case self.btn_save:
                self.func_save_img()
            case self.btn_view:
                self.func_view()
            case self.btn_default:
                self.func_default()

    def func_make(self):#最重要的函数。包含解析、检查、生成，3个过程。
        print(self.ls,self.pm,self.el)

        self.proc_reset()
        self.btns_reset()
        self.current_gen_img=None

        #stage1
        self.lb_proc.setText("解析")
        data=htm2list(self.current_src)
        if(data):
            self.proc_bar.setValue(1)
            self.lb_proc.setText(self.colored_qlb_text(self.lb_proc.text(),"green"))
        else:
            self.lb_proc.setText(self.colored_qlb_text(self.lb_proc.text(),"red"))
            self.message_browser.append("源文件解析失败。")
            self.message_browser.moveCursor(QTexCursor.End)
            return None

        #stage2
        self.lb_proc.setText("检查")
        check=full_check2(data)
        match check:
            case 0:
                self.proc_bar.setValue(2)
                self.lb_proc.setText(self.colored_qlb_text(self.lb_proc.text(),"green"))
            case (2,_):
                self.lb_proc.setText(self.colored_qlb_text(self.lb_proc.text(),"red"))
                self.message_browser.append("源文件中所用字体存在错误。")
                self.message_browser.moveCursor(QTextCursor.End)

                for i in check[1]:
                    self.message_browser.append(str(i))
                    self.message_browser.moveCursor(QTextCursor.End)
                return None
            case 1:
                self.lb_proc.setText(self.colored_qlb_text(self.lb_proc.text(),"red"))
                self.message_browser.append("源文件中数据为空。")
                self.message_browser.moveCursor(QTextCursor.End)
                return None
            case (3,_):
                self.lb_proc.setText(self.colored_qlb_text(self.lb_proc.text(),"red"))
                self.message_browser.append("运用了不支持的字符。")
                self.message_browser.moveCursor(QTextCursor.End)

                for i in check[1]:
                    self.message_browser.append(str(i))
                    self.message_browser.moveCursor(QTextCursor.End)
                return None

        #stage3
        self.lb_proc.setText("生成")
        self.current_gen_img=img_generate(data,ls=self.ls,pm=self.pm,el=self.el)
        if(self.current_gen_img):
            self.proc_bar.setValue(3)
            self.lb_proc.setText(self.colored_qlb_text(self.lb_proc.text(),"green"))
            self.btn_save.setEnabled(True)
            self.btn_view.setEnabled(True)
        else:
            self.lb_proc.setText(self.colored_qlb_text(self.lb_proc.text(),"red"))
            self.message_browser.append("图片生成过程中出现错误。")
            self.message_browser.moveCursor(QTextCursor.End)
            return None

    def func_save_img(self):
        output_dir=Path.cwd().parent / "output"
        (save_path,filter)=QFileDialog.getSaveFileName(self,"另存为",str(output_dir),"*.png")
        self.current_gen_img.save(save_path)

    def func_view(self):
        self.current_gen_img.show()

    def func_default(self):
        self.qsb_ls.setValue(2)
        for i in (self.qsb_pm_x,self.qsb_pm_y):
            i.setValue(5)
        self.qsb_el.setValue(32)

    def set_current_src(self,src):#传入源文件所用函数
        self.current_src=src
        self.setWindowTitle("图像生成器-当前文件“{0:s}”".format(self.current_src))

    def colored_qlb_text(self,text,color):#给HTML文本上色(QLabel用的也是HTML文本)
        return '<span style="color:{0:s}">{1:s}</span>'.format(color,text)

    def func_qsb_chenged(self):#一旦参数被调过，立刻更新变量值
        self.ls=self.qsb_ls.value()
        self.pm=(self.qsb_pm_x.value(),self.qsb_pm_y.value())
        self.el=self.qsb_el.value()
