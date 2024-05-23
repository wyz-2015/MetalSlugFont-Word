from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sqlite3
from pathlib import Path

class SKeyboard(QWidget):
    key_out=pyqtSignal(str)
    def __init__(self):
        super(SKeyboard,self).__init__()
        self.setWindowTitle("符号软键盘")
        icon=Path.cwd() / "static" / "assets" / "fonts" / "font-1" / "ms-blue" / "letters" / "upper-case" / "K.png"
        self.setWindowIcon(QIcon(str(icon)))
        
        db_path=Path.cwd() / "static" / "assets" / "fonts" / "supported_chars.db"
        self.sql_con=sqlite3.connect(str(db_path))
        self.sql_cur=self.sql_con.cursor()

        self.current_font_id=None

        self.keys=[]
        self.get_symbol_keys()
        self.show_keys()
        
    def get_symbol_keys(self):#从数据库中获取所有“符号”字符
        res=self.sql_cur.execute("SELECT char,chars.name FROM chars JOIN types ON chars.type_id=types.id WHERE types.name='symbols'")
        for (char,name) in res.fetchall():
            btn=QPushButton()
            btn.setText(char)
            btn.setToolTip(name)
            btn.setFixedSize(40,40)
            #print(char)
            #btn.clicked.connect(lambda:self.key_out.emit(char))
            f=self.f_returner(char)
            btn.clicked.connect(f)#不能用lambda，只能传一个写“死”的函数进去，否则只会传出最后一项的char值
            self.keys.append(btn)

    def show_keys(self):#排列各键，并设定QWidget控件
        v_layout=QVBoxLayout()
        
        flag=True
        i=0
        while(flag):
            h_layout=QHBoxLayout()
            j=0
            while(j<10):
                h_layout.addWidget(self.keys[i])
                i+=1
                if(not i<len(self.keys)):
                    flag=False
                    break
                j+=1
            v_layout.addLayout(h_layout)

        self.setLayout(v_layout)

    def set_font_id(self,_id):#一旦self.current_font_id被修改，随即更新各键的可用情况
        self.current_font_id=_id
        self.set_keys_enabled()

    def set_keys_enabled(self):#设定各键的可用情况。可随主窗口中“当前字体”的设定而灵活更新
        res=self.sql_cur.execute("SELECT in_font{0:n} FROM chars JOIN types ON chars.type_id=types.id WHERE types.name='symbols'".format(self.current_font_id))
        temp=res.fetchall()
        for i in range(len(temp)):
            if(temp[i][0]):
                self.keys[i].setEnabled(True)
            else:
                self.keys[i].setEnabled(False)

    def f_returner(self,c):
        def f():
            self.key_out.emit(c)

        return f
