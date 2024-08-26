from PIL import Image
from pathlib import *
import argparse
from checker import full_check2,htm_format_to_font_id
from src_parser import htm2list
import sqlite3
import sys

def sqlEscapeChar(c):#在需要时转换字符，以能在SQL表达式中正确使用。
    if(c=="'"):
        return "'{0:s}".format(c)
    else:
        return c

class Cursor():
    def __init__(self):
        (self.x,self.y)=(0,0)
        self.page_margins=(5,5)
        self.line_specing=2
        self.empty_line=32
        #空字符长需要取决于对应字体

    def start(self):#reset
        (self.x,self.y)=(0,0)
        (dx,dy)=self.page_margins
        self.x+=dx
        self.y+=dy

    def set_page_margins(self,xy):
        self.page_margins=xy

    def set_line_specing(self,ls):
        self.line_specing=ls

    def set_empty_line(self,el):
        self.empty_line=el

    def mv_next_char(self,char_width):
        self.x+=char_width

    def mv_return(self):
        #self.y+=self.line_specing
        self.x=self.page_margins[0]

    def create_line(self,l_height):
        self.y+=l_height

    def mv_empty_line(self):
        self.y+=self.empty_line

    def mv_line_specing(self):
        self.y+=self.line_specing

    def get_xy(self):
        return (self.x,self.y)

class Painter():
    def __init__(self):
        self.data=None
        self.cur=Cursor()
        self.canvas=Image.new("RGBA",(1,1),(0,0,0,0))
        #self.page_margins=(2,2)
        #self.line_specing=1
        self.cur.start()

        db_path=Path.cwd() / "static" / "assets" / "fonts" / "supported_chars.db"
        self.sql_con=sqlite3.connect(str(db_path))
        self.sql_cur=self.sql_con.cursor()

        self.fonts_dir=Path.cwd() / "static" / "assets" / "fonts"

    def set_data(self,data):
        self.data=data

    def get_line_height(self,line):
        max_height=0
        for block in line:
            font_id=htm_format_to_font_id(block)
            res=self.sql_cur.execute("SELECT max(height) FROM font{0:n}_chars_size".format(font_id))
            max_height=max(max_height,res.fetchall()[0][0])

        return max_height

    def get_char_size(self,c,font_id):
        c=sqlEscapeChar(c)
        res=self.sql_cur.execute("SELECT width,height FROM chars JOIN font{0:n}_chars_size ON chars.name=font{0:n}_chars_size.name WHERE char='{1:s}'".format(font_id,c))

        return res.fetchone()

    def select_char(self,c,font_id,color):#活 字 印 刷 术
        c=sqlEscapeChar(c)
        res=self.sql_cur.execute("SELECT chars.name,types.name FROM chars JOIN types ON chars.type_id=types.id WHERE char='{0:s}'".format(c))
        (char_name,char_type)=res.fetchone()

        if(char_type=="letter-upper"):
            char_type="letters/upper-case"
        elif(char_type=="letter-lower"):
            char_type="letters/lower-case"

        return self.fonts_dir / "font-{0:n}".format(font_id) / "ms-{0:s}".format(color) / char_type / "{0:s}.png".format(char_name)

    def putchar(self,c,font_id,color):
        (x,y)=self.cur.get_xy()
        #print("光标：({0:n},{1:n})".format(x,y))

        #(dx,dy)=self.get_char_size(c,font_id)
        #(temp_x,temp_y)=(x+dx+self.page_margins[0],y+dy+self.page_margins[1])
        #temp_x=x+dx+self.cur.page_margins[0]
        #if(temp_x>self.canvas.size[0]):
        #    self.canvas=self.canvas.resize((temp_x,self.canvas.size[1]))
        #if(temp_y>self.canvas.size[1]):
        #    self.canvas=self.canvas.resize((self.canvas.size[0],temp_y))
        #画布大小只能事前确定，不能灵活变动，否则后来打印的字符将错位。弃用。

        (xc,yc)=self.get_char_size(c,font_id)

        if(c!=" "):
            #print(xc,y-yc)
            img=Image.open(str(self.select_char(c,font_id,color)))
            img=img.convert("RGBA")
            #print(img,str(self.select_char(c,font_id,color)))
            #img.show()
            #self.canvas.paste(img,(x,y-yc),img.convert("L"))
            self.canvas.paste(img,(x,y-yc))
            #self.canvas.show()
            self.cur.mv_next_char(xc)
        else:
            self.cur.mv_next_char(xc)

    def puts(self,line):
        if(line):
            l_height=self.get_line_height(line)
            self.cur.create_line(l_height)
            
            #temp_y=self.cur.page_margins[1]+l_height+self.cur.y
            #if(temp_y>self.canvas.size[1]):
            #    self.canvas=self.canvas.resize((self.canvas.size[0],temp_y))
            
            for block in line:
                font_id=htm_format_to_font_id(block)
                color=block["color"]
                text=block["text"]
                for c in text:
                    self.putchar(c,font_id,color)

            self.cur.mv_return()
        else:
            self.cur.mv_empty_line()

    def calc_canvas_size(self):
        (X,Y)=self.cur.page_margins

        for line in range(len(self.data)-1):
            v_line=self.data[line]
            if(v_line):
                Y+=self.get_line_height(v_line)
                if(self.data[line+1]):
                    Y+=self.cur.line_specing
            else:
                Y+=self.cur.empty_line
        final_line=self.data[-1]
        if(final_line):
            Y+=self.get_line_height(final_line)
        else:
            Y+=self.cur.empty_line
        Y+=self.cur.page_margins[-1]

        for line in self.data:
            X1=self.cur.page_margins[0]
            for block in line:
                text=block["text"]
                font_id=htm_format_to_font_id(block)
                for c in text:
                    X1+=self.get_char_size(c,font_id)[0]
            X1+=self.cur.page_margins[0]
            X=max(X,X1)

        self.canvas=self.canvas.resize( (X,Y) )

        #print(X,Y)
        return (X,Y)

    def paint_all(self):
        for line in range(len(self.data)-1):
            v_line=self.data[line]
            self.puts(v_line)
            if(v_line and self.data[line+1]):
                self.cur.mv_line_specing()

        final_line=self.data[-1]
        self.puts(final_line)

def img_generate(data,ls=None,pm=None,el=None):#行距,页边距(x,y),空行大小
    p=Painter()
    if(ls and pm and el):
        if(ls):
            p.cur.set_line_specing(ls)
        if(pm):
            p.cur.set_page_margins(pm)
        if(el):
            p.cur.set_empty_line(el)

        p.cur.start()
    #p.cur.y+=40
    #print(p.sql_cur.execute("select * from chars").fetchall())
    #print(p.get_char_size("×",1))
    #p.putchar("A",1,"blue")
    #data=htm2list(src_path)
    p.set_data(data)
    p.calc_canvas_size()
    #p.puts(data[0])
    p.paint_all()
    
    return p.canvas

if(__name__=="__main__"):
    cmd_parser=argparse.ArgumentParser(epilog="我是负责生成图片的。确实，我的工作量是最大的。\n如果你能叫我sensei，我其实会更高兴，谢谢你。( ゜- ゜)つロ",description="绘制娘(=・ω・=)")
    cmd_parser.add_argument("input_file",help="传入的html格式的源文件，这个一定要有哦~")#,required=True)
    cmd_parser.add_argument("-o","--ouput_path",help="输出的png图片的路径和文件名，例如“./114514/1919810.png”。如果没有指定这个的话，我只能帮你在原地生成一个叫作“a.out.png”的文件了……",required=False,default="a.out.png",dest="output_path")
    cmd_parser.add_argument("-ls","--line_specing",help="设定行距，数值得是整数哦~",required=False,dest="ls",type=int)
    cmd_parser.add_argument("-pm","--page_margins",help="设定页边距，左右、上下，两个整数。请用半角逗号“,”分割。",required=False,dest="pm",type=lambda x:[int(i) for i in x.split(",")])
    cmd_parser.add_argument("-el","--empty_line",help="设定空行高度，目前只能全局设定空行的高度。数值得是整数哦~",required=False,dest="el",type=int)
    
    args=cmd_parser.parse_args()
    #print(args)

    (ls,pm,el)=(args.ls,args.pm,args.el)
    data=htm2list(args.input_file)

    if(not data):
        print("未能成功解析源文件的内容。(src_parser.py)")
        sys.exit(1)

    bads=full_check2(data)
    match bads:
        case 1:
            print("源文件中数据为空。(checker.py)")
            sys.exit(1)
        case (2,_):
            print("源文件中所用字体存在错误。(checker.py)")
            for i in bads[1]:
                print(i)
            sys.exit(2)
        case (3,_):
            print("运用了不支持的字符。(checker.py)")
            for i in bads[1]:
                print(i)
            sys.exit(3)
    img=img_generate(data,ls=ls,pm=pm,el=el)
    img.save(args.output_path)
