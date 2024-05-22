from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from pathlib import *
#import os
from image_generator_gui import Img_gen_gui

class MainWindow(QMainWindow):#主窗口
    def __init__(self):
        super(MainWindow,self).__init__()
        self.resize(800,600)
        self.setWindowTitle("欢迎使用 -- MetalSlugFont-Word")

        icon=Path.cwd() / "static" / "assets" / "fonts" / "font-1" / "ms-blue" / "letters" / "upper-case" / "W.png"
        self.setWindowIcon(QIcon(str(icon)))

        self.current_file=None#当前文件(path)
        self.current_file_unsave=False#当前文件未保存？

        #### 工具栏1 ####
        self.toolbar_fileio=ToolBar_FileIO()
        self.addToolBar(Qt.TopToolBarArea,self.toolbar_fileio)
        self.toolbar_fileio.signal.connect(self.toolbar_fileio_signal_center)

        #### 工具栏2 ####
        self.toolbar_text_format=ToolBar_Text_Format()
        self.addToolBar(Qt.TopToolBarArea,self.toolbar_text_format)
        self.toolbar_text_format.font_changed.connect(self.func_change_font)
        self.toolbar_text_format.actions_signal.connect(self.toolbar_fileio_signal_center)
        #self.toolbar_text_format

        self.current_font_id=None #为了“应用字体设置”功能增加的变量
        self.current_font_color=None

        #### 编辑框 ####
        self.edit_area=QTextEdit()
        self.edit_area.setLineWrapMode(QTextEdit.NoWrap)
        self.func_change_font( (1,QColor("blue")) )
        self.setCentralWidget(self.edit_area)
        self.edit_area.textChanged.connect(self.func_text_changed)

        #### 菜单栏 ####
        self.menu_bar=MenuBar()
        self.setMenuBar(self.menu_bar)
        self.menu_bar.signal.connect(self.toolbar_fileio_signal_center)

    #### 工具栏1 ####
    def toolbar_fileio_signal_center(self,signal):#名义上是工具栏1的，实则为编辑器全局实用的信号处理中心。
        print(signal)
        match signal:
            case "open":
                self.func_open_action()
            case "new":
                self.func_new_action()
            case "save":
                self.func_save_action()
            case "save_as":
                self.func_save_as_action()
            case "undo":
                self.func_undo_action()
            case "redo":
                self.func_redo_action()
            case "make":
                self.func_make_action()
            case "apply":#新增
                self.func_change_font( (self.current_font_id,self.current_font_color) )
            # 除了工具栏以外的部分
            case "soft_keyboard":
                self.func_soft_keyboard()
            case "about":
                self.func_about_action()
            case "exit":
                self.func_exit_action()

    def func_open_action(self):#打开文件
        (file_path,filter)=QFileDialog.getOpenFileName(self,"打开文件","./","")
        if(file_path):
            print("打开了：{0:s}".format(file_path))
            self.current_file=file_path
            src_file=open(self.current_file,"r")
            self.edit_area.setHtml(src_file.read())
            src_file.close()
            
            self.current_file_unsave=False
            self.change_window_title(self.current_file)

    def func_new_action(self):#“新建，清空当前QTextEdit”
        self.current_file=None
        self.current_file_unsave=False #然而还是会显示为“未保存”，因为clear()方法本身也被算作了一次“修改”
        self.edit_area.clear()

    def func_save_action(self):#如果已打开某个文件，则直接保存。反之则“另存为”并设定为当前打开文件。
        if(self.current_file):
            src_file=open(self.current_file,"w")
            src_file.write(self.edit_area.toHtml())
            src_file.close()

            self.current_file_unsave=False
            self.change_window_title(self.current_file)
        else:
            self.func_save_as_action()

    def func_save_as_action(self):
        save_dir=Path.cwd().parent / "input"
        (save_path,filter)=QFileDialog.getSaveFileName(self,"另存为",str(save_dir),"")
        print("另存至：{0:s}".format(save_path))
        if(save_path):
            src_file=open(save_path,"w")
            src_file.write(self.edit_area.toHtml())
            src_file.close()
            self.current_file=save_path

            self.current_file_unsave=False
            self.change_window_title(self.current_file)

    def func_undo_action(self):
        self.edit_area.undo()

    def func_redo_action(self):
        self.edit_area.redo()

    def func_make_action(self):#调用图像生成器前端
        self.generator_gui=Img_gen_gui()
        self.generator_gui.set_current_src(self.current_file)
        self.generator_gui.show()

    ###################

    #### 工具栏2 ####
    def func_change_font(self,setting):
        (font_id,font_color)=setting
        (self.current_font_id,self.current_font_color)=setting #新增
        #print(setting)
        self.edit_area.setCurrentCharFormat(get_editor_font(font_id))
        self.edit_area.setTextColor(font_color)

    def func_soft_keyboard(self):
        QMessageBox.information(self,"TODO","该功能尚未完成，敬请期待~",QMessageBox.Yes)

    ###################

    #### 编辑区 ####
    def func_text_changed(self):
        self.current_file_unsave=True
        self.change_window_title(self.current_file)

    ###################

    #### 菜单栏 ####
    def func_exit_action(self):
        if(self.current_file_unsave):
            choice=QMessageBox.question(self,"确认保存与退出","当前文档“{0}”尚未保存，是否保存或退出？\n“是”：保存并退出；“否”：不保存并退出；“取消”：不退出".format(self.current_file),QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            match choice:
                case QMessageBox.Yes:
                    self.func_save_action()
                    sys.exit(0)
                case QMessageBox.No:
                    sys.exit(0)
        else:
            sys.exit(0)

    def func_about_action(self):
        QMessageBox.about(self,"关于","版本：0.1\nGithub仓库：https://github.com/wyz-2015/MetalSlugFont-Word\n复刻分支作者：wyz_2015")

    def change_window_title(self,file_path):
        if(file_path):
            file=Path(file_path)
            file_name=file.name
        else:
            file_name="未保存文件"

        self.setWindowTitle("{0}{1} -- MetalSlugFont-Word".format(file_name, ("*" if(self.current_file_unsave) else "") ))

    def closeEvent(self,event):
        if(self.current_file_unsave):
            choice=QMessageBox.question(self,"确认保存与退出","当前文档“{0}”尚未保存，是否保存或退出？\n“是”：保存并退出；“否”：不保存并退出；“取消”：不退出".format(self.current_file),QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            match choice:
                case QMessageBox.Yes:
                    self.func_save_action()
                    event.accept()
                case QMessageBox.No:
                    event.accept()
                case QMessageBox.Cancel:
                    event.ignore()
        else:
            event.accept()

class MenuBar(QMenuBar):#控件在外面画好，功能在里面定义
    signal=pyqtSignal(str)
    def __init__(self):
        super(MenuBar,self).__init__()
        #toolbar1=QToolBar("输入与输出")
        #toolbar2=QToolBar("文字格式调整")
        self.file_menu=self.addMenu("文件")
        self.edit_menu=self.addMenu("编辑")
        #self.format_menu=self.addMenu("格式")
        self.tools_menu=self.addMenu("工具")
        self.help_menu=self.addMenu("帮助")

        #### 各个工具 ####
        open_action=QAction(QIcon("./icons/document-open.svg"),"打开",self)
        open_action.triggered.connect(lambda : self.signal.emit("open"))
        new_action=QAction(QIcon("./icons/document-new.svg"),"新建/清空",self)
        new_action.triggered.connect(lambda : self.signal.emit("new"))
        save_action=QAction(QIcon("./icons/document-save.svg"),"保存",self)
        save_action.triggered.connect(lambda : self.signal.emit("save"))
        save_as_action=QAction(QIcon("./icons/document-save-as.svg"),"另存为",self)
        save_as_action.triggered.connect(lambda : self.signal.emit("save_as"))
        redo_action=QAction(QIcon("./icons/edit-redo.svg"),"重做",self)
        redo_action.triggered.connect(lambda : self.signal.emit("redo"))
        undo_action=QAction(QIcon("./icons/edit-undo.svg"),"撤销",self)
        undo_action.triggered.connect(lambda : self.signal.emit("undo"))
        make_action=QAction(QIcon("./icons/media-playback-start.svg"),"生成图片",self)
        make_action.triggered.connect(lambda : self.signal.emit("make"))

        exit_action=QAction("退出",self)
        exit_action.triggered.connect(lambda : self.signal.emit("exit"))
        soft_keyboard_action=QAction(QIcon("./icons/percent.svg"),"符号软键盘",self)
        soft_keyboard_action.triggered.connect(lambda : self.signal.emit("soft_keyboard"))
        about_action=QAction("关于",self)
        about_action.triggered.connect(lambda : self.signal.emit("about"))
        ##################

        ## 文件 ##
        self.file_menu.addActions([new_action,open_action])
        self.file_menu.addSeparator()
        self.file_menu.addActions([save_action,save_as_action])
        self.file_menu.addSeparator()
        self.file_menu.addAction(make_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(exit_action)

        ## 编辑 ##
        self.edit_menu.addActions([undo_action,redo_action])

        ## 工具 ##
        self.tools_menu.addAction(soft_keyboard_action)

        ## 帮助 ##
        self.help_menu.addAction(about_action)

class ToolBar_FileIO(QToolBar):
    signal=pyqtSignal(str)

    def __init__(self):
        super(ToolBar_FileIO,self).__init__()
        self.setWindowTitle("输入与输出")
        
        #### 各个工具 ####
        open_action=QAction(QIcon("./icons/document-open.svg"),"打开",self)
        open_action.triggered.connect(lambda : self.signal.emit("open"))
        new_action=QAction(QIcon("./icons/document-new.svg"),"新建/清空",self)
        new_action.triggered.connect(lambda : self.signal.emit("new"))
        save_action=QAction(QIcon("./icons/document-save.svg"),"保存",self)
        save_action.triggered.connect(lambda : self.signal.emit("save"))
        save_as_action=QAction(QIcon("./icons/document-save-as.svg"),"另存为",self)
        save_as_action.triggered.connect(lambda : self.signal.emit("save_as"))
        redo_action=QAction(QIcon("./icons/edit-redo.svg"),"重做",self)
        redo_action.triggered.connect(lambda : self.signal.emit("redo"))
        undo_action=QAction(QIcon("./icons/edit-undo.svg"),"撤销",self)
        undo_action.triggered.connect(lambda : self.signal.emit("undo"))
        make_action=QAction(QIcon("./icons/media-playback-start.svg"),"生成图片",self)
        make_action.triggered.connect(lambda : self.signal.emit("make"))
        ##################

        for widget in (new_action,open_action,save_action,save_as_action,undo_action,redo_action,make_action):
            self.addAction(widget)

        self.setAllowedAreas(Qt.AllToolBarAreas)
        self.setMovable(True)

class ToolBar_Text_Format(QToolBar):
    font_changed=pyqtSignal(tuple)
    actions_signal=pyqtSignal(str)
    def __init__(self):
        super(ToolBar_Text_Format,self).__init__()
        #self.example_icons=Example_icons()
        
        #### 选择字体 ####
        self.font_type_combo_box=QComboBox()
        self.font_type_combo_box.setIconSize(QSize(100,15))
        #font_type_combo_box_items=[
        #        (QIcon("./static/assets/examples/ms-font-1/Blue.png"),"一般"),
        #        (QIcon("./static/assets/examples/ms-font-2/Blue.png"),"细体"),
        #        (QIcon("./static/assets/examples/ms-font-3/Blue.png"),"高体"),
        #        (QIcon("./static/assets/examples/ms-font-4/Blue.png"),"大体"),
        #        (QIcon("./static/assets/examples/ms-font-5/Blue.png"),"大橙体")
        #        ]
        font_type_combo_box_items=(
                (get_icon(1,"Blue"),"一般"),
                (get_icon(2,"Blue"),"细体"),
                (get_icon(3,"Blue"),"高体"),
                (get_icon(4,"Blue"),"大体"),
                (get_icon(5,"Orange"),"过关体"),
                )
        for (icon,text) in font_type_combo_box_items:
            self.font_type_combo_box.addItem(icon,text)

        self.font_type_combo_box.currentIndexChanged.connect(self.update_font_color_combo_box_list)

        ###############

        #### 选择颜色 ####
        self.font_color_combo_box=QComboBox()
        self.font_color_combo_box.setIconSize(QSize(100,15))
        self.update_font_color_combo_box_list()#初始化
        self.font_color_combo_box.currentTextChanged.connect(self.send_format_setting)
        ################

        #### 应用当前格式 ####
        self.apply_format_action=QAction(QIcon("./static/assets/fonts/font-1/ms-blue/letters/upper-case/A.png"),"应用当前格式",self)
        self.apply_format_action.triggered.connect( lambda : self.actions_signal.emit("apply") )

        #### 软键盘 ####
        self.soft_keyboard=QAction(QIcon("./icons/percent.svg"),"符号软键盘",self)
        self.soft_keyboard.triggered.connect( lambda : self.actions_signal.emit("soft_keyboard") )
        ######################

        self.addWidget(self.font_type_combo_box)
        self.addWidget(self.font_color_combo_box)
        self.addAction(self.apply_format_action)
        self.addAction(self.soft_keyboard)

    def update_font_color_combo_box_list(self):
        self.font_color_combo_box.clear()
        match (self.font_type_combo_box.currentIndex()+1):#众所周知，index是从0开始数的，故+1
            case 1:
                items=(
                        (get_icon(1,"Blue"),"蓝色"),
                        (get_icon(1,"Gold"),"金色"),
                        (get_icon(1,"Orange"),"橙色"),
                        )
            case 2:
                items=(
                        (get_icon(2,"Blue"),"蓝色"),
                        (get_icon(2,"Gold"),"金色"),
                        (get_icon(2,"Orange"),"橙色"),
                        )
            case 3:
                items=(
                        (get_icon(3,"Blue"),"蓝色"),
                        (get_icon(3,"Orange"),"橙色"),
                        )
            case 4:
                items=(
                        (get_icon(4,"Blue"),"蓝色"),
                        (get_icon(4,"Yellow"),"黄色"),
                        (get_icon(4,"Orange"),"橙色"),
                        )
            case 5:
                items=(
                        (get_icon(5,"Orange"),"橙色"),
                        )

        for (icon,item) in items:
            self.font_color_combo_box.addItem(icon,item)

        self.send_format_setting()

    def send_format_setting(self):#编制信号，发到主窗口类里，再利用
        (font_id,color)=(self.font_type_combo_box.currentIndex()+1,self.font_color_combo_box.currentText())
        color_dict={"蓝色":"blue","金色":"gold","黄色":"yellow","橙色":"orange"}
        if(font_id and color):
            self.font_changed.emit( (font_id,QColor(color_dict[color])) )

def get_icon(font_id,font_color):
    examples_dir=Path.cwd() / "static" / "assets" / "examples"

    icon=QIcon()
    #image_path="{0:s}/ms-font-{1:n}/{2:s}.png".format(str(self.examples_dir),font_id,font_color)
    image_path=examples_dir / "ms-font-{0:n}".format(font_id) / "{0:s}.png".format(font_color)
    #print(image_path)
    icon.addFile(str(image_path))

    return icon

def get_editor_font(font_id):#编辑器中使用的字体的设置
    font1={"name":"CascadiaCodePL.ttf","bold":75,"size":32}
    font2={"name":"Laksaman-Italic.ttf","bold":40,"size":32}
    font3={"name":"OpenSans-CondLight.ttf","bold":75,"size":48}
    font4={"name":"FreeSansBold.otf","bold":75,"size":64}
    font5={"name":"FreeSerifBoldItalic.otf","bold":100,"size":50}

    editor_fonts_dir=Path.cwd() / "fonts4editor"
    editor_fonts={
            1:font1,
            2:font2,
            3:font3,
            4:font4,
            5:font5
            }
           
    font_file_path =str( editor_fonts_dir / editor_fonts[font_id]["name"] )
    # 加载字体到数据库  
    id_ = QFontDatabase.addApplicationFont(font_file_path)  
    # 获取字体的家族名称（如果知道确切名称，也可以直接使用）  
    family = QFontDatabase.applicationFontFamilies(id_)[0]  
    # 创建QFont对象并设置字体大小和样式  
    font = QFont(family, editor_fonts[font_id]["size"])  

    text_char_font=QTextCharFormat()
    text_char_font.setFont(font)
    text_char_font.setFontWeight(editor_fonts[font_id]["bold"])

    return text_char_font

if(__name__=="__main__"):
    #app=QApplication(sys.argv)
    #window=MainWindow()
    #window.show()
    #sys.exit(app.exec())
    sys.exit("别看我，我没有台词……")
