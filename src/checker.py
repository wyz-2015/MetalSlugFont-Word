import sqlite3
from pathlib import Path
from src_parser import htm2list
import sys
import argparse

class Checker():#检查器，检查富文本是否是规定的几种格式之一。不属于其中的，无法被生成图片。
    def __init__(self,data):
        self.conn=None
        self.data=data

    def connect_dbms(self,db_path):#链接数据库，引入sqlite3解决了“字体中到底支持哪些字”“那些字的长宽都是多少”“哪个字最高”“页宽计算”等等问题
        self.conn=sqlite3.connect(db_path)
        self.c=self.conn.cursor()

    def get_support_chars_set(self,font_id):#获取字体n中支持的所有字符，附带名字、类型信息。
        sql_expression="select chars.name as name,char,types.name as type from chars join types on types.id=chars.type_id where chars.in_font{0}=1".format(font_id)
        res=self.c.execute(sql_expression)
        
        return [{"name":name,"char":char,"type":_type} for (name,char,_type) in res]

    def char_check(self):#想要检查字符，必先检查字体。
        bads=[]

        #if(self.empty_check()):
        #    return 1#没有获取到数据或者数据为空

        for line in range(len(self.data)):
            r_line=self.data[line]
            #print(r_line)
            if(r_line):#如果是空行则跳过
                for block in range(len(r_line)):
                    r_block=r_line[block]
                    #print("\t",r_block)
                    font_id=htm_format_to_font_id(r_block)
                    char_set={ i["char"] for i in self.get_support_chars_set( font_id ) }#获取当前block对应font的可用字体集
                    for num_char in range(len(r_block["text"])):
                        r_char=r_block["text"][num_char]
                        #print("\t\t",r_char)
                        if(not (r_char in char_set) ):
                            bads.append( {"line":line+1,"block":block+1,"num_char":num_char+1,"char":r_char,"font_id":font_id} )

        if(bads):
            return bads
        else:
            return 0#检查无误

    def font_check(self):#检查富文本是否都是规定之内的
        bads=[]

        #if(self.empty_check()):
        #    return 1#没有获取到数据或者数据为空

        for line in range(len(self.data)):
            r_line=self.data[line]
            #print(r_line)
            if(r_line):#如果是空行则跳过
                for block in range(len(r_line)):
                    r_block=r_line[block]
                    if(not htm_format_to_font_id(r_block)):
                        bads.append( {"line":line+1,"block":block+1} )

        if(bads):
            return bads
        else:
            return 0#检查无误

    def empty_check(self):#检查传入数据是否为全空或只有空行
        if(not self.data):
            return True

        for i in self.data:
            if(i):
                return False
        
        return True

def htm_format_to_font_id(block):#在多个地方都被调用的函数。放这里只是因为一开始是在这里编写的，本来是Check()下的方法，后独立为函数
    match (block["font-family"],block["font-size"],block["font-weight"]):
        case ("Cascadia Code PL","32pt","600"):
            return 1
        case ("Laksaman","32pt","320"):
            return 2
        case ("Open Sans","48pt","600"):
            return 3
        case ("FreeSans","64pt","600"):
            return 4
        case ("FreeSerif","50pt","800"):
            return 5

def full_check2(data):#主要函数
    #checker=Checker(htm2list(src_path))
    checker=Checker(data)
    db_path=Path.cwd() / "static" / "assets" / "fonts" / "supported_chars.db"
    checker=Checker(data)
    checker.connect_dbms(db_path)

    if(checker.empty_check()):
        return 1#数据为空
    else:
        fc=checker.font_check()
        if(fc):
            return (2,fc)#字体错误
        else:
            cc=checker.char_check()
            if(cc):
                return (3,cc)#字符错误
            else:
                return 0#无误

def full_check(src_path):#彩蛋模式用
    db_path=Path.cwd() / "static" / "assets" / "fonts" / "supported_chars.db"
    #print(db_path)
    data=htm2list(src_path)
    #print(data)
    checker=Checker(data)
    checker.connect_dbms(db_path)

    #print(checker.full_check())
    #print(len(checker.get_support_chars_set(1)),len(checker.get_support_chars_set(2)))

    #(fc,cc)=(checker.font_check(),checker.char_check())
    if(checker.empty_check()):
        print("{0:s}: 笨蛋，你(TM)就给本小姐看这个什么都没有的东西？ヽ(`Д´)ﾉ".format(red_str("error")))
        error_exit()
    else:
        fc=checker.font_check()#先判断字体是否正确

        if(fc==0):
            print("源文件中的字体信息，均能映射到所支持的字体，没有问题！")

            cc=checker.char_check()#再判断字符是否正确
            if(cc and cc!=1):
                print("{0:s}: 杂鱼~杂鱼~你用了字库里没有的字符啦~(ಡωಡ)".format(red_str("error")))
                for i in cc:
                    print("\t第{0:n}行，第{1:n}个block，其中第{2:n}个字符“{3:s}”，用的是{4:n}号字体库。".format(i["line"],i["block"],i["num_char"],i["char"],i["font_id"]))
                error_exit()

            else:
                print("源文件中的内容的所用字符，均为支持的字符，没有问题！")

                print("很好！本小姐单方面宣布：你的源文件没有问题！✧(≖ ◡ ≖✿)")

        else:
            print("{0:s}: 杂鱼~杂鱼~你这这些block用的格式，哇木栽呀啦~(ಡωಡ)".format(red_str("error")))
            for i in fc:
                print("\t第{0:n}行，第{1:n}个block。".format(i["line"],i["block"]))
                error_exit()


def error_exit():
    print("如果你觉得我对你源文件里写的没理解对，那你应该去找我姐，源文件解析娘，“src_parser.py”。我所检查的信息都是她预先处理过，再给我的。")
    sys.exit(1)

def red_str(s):#改变终端中输出字符串的颜色，同时不去引入其他模块。
    #return "".join([("\033[31m"+c) for c in s])
    return "\033[31m"+s+"\033[0m"

if(__name__=="__main__"):
    cmd_parser=argparse.ArgumentParser(epilog="我！帮你检查源文件里有没有不对的字体和不支持的字符的！要是我这关过不去，你也别想请我姐绘制娘(image_generator.py)帮你生成图片了~\n我已经等不及了，快点端上来吧！ε=ε=(ノ≧∇≦)ノ",description="检查娘✿ヽ(°▽°)ノ✿")
    cmd_parser.add_argument("input_file")
    input_file=cmd_parser.parse_args().input_file

    full_check(input_file)
