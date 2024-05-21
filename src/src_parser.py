from html.parser import HTMLParser
import argparse

class Parser(HTMLParser):#分析由QTextEdit控件生成的HTML文件
    def __init__(self):
        super(Parser,self).__init__()
        self.data=[]
        self.line=[]
        self.found_span=False

    def handle_starttag(self,tag,attrs):#逢“p”标记开新行，逢“span”标记就在新行中开始记录参数与文本，称作“Block”。
        match tag:
            case "p":
                self.line.clear()
            case "span":
                self.temp_block=Block()
                self.temp_block.set_attrs(attrs)
                self.found_span=True
             
    def handle_data(self,data):
        if(self.found_span):
            self.temp_block.text=data

    def handle_endtag(self,tag):
        match tag:
            case "p":
                self.data.append(self.line.copy())
            case "span":
                self.line.append(self.temp_block)
                self.found_span=False

    def get_result(self):
        return self.data.copy()

class Block():#接收并分析上文html解析器所得数据，顾名思义，一个Block()存储一段连续的使用相同格式的富文本。
    def __init__(self):
        self.text=None
        self.font=None
        self.color=None
        self.attrs=None

        self.color_dict={"#0000ff":"blue","#ffa500":"orange","#ffd700":"gold","#ffff00":"yellow"}

    def set_attrs(self,attrs):
        self.attrs=attrs

    def set_text(self,text):
        self.text=text

    def get_data(self):
        data=self.analyse_style_attrs(self.attrs)
        data["text"]=self.text

        return data

    def analyse_style_attrs(self,attr):#繁杂的字符串解析
        attr1=attr[0][-1]
        attr_group=attr1.split(";")
        #print(f"{attr1=}\n{attr_group=}")
        
        sttr_dict=dict()
        for kv in attr_group[:-1]:#最后一位是空字符串""，故去掉
            #print(kv)
            (k,v)=kv.split(":")
            k=k.strip()
            v=v.strip()
            match k:
                case "font-family":
                    v=v.strip("'")
                case "color":
                    v=self.color_dict[v]

            sttr_dict[k]=v

        return sttr_dict

    def __str__(self):
        #return "内容：{0}\t参数：{1}".format(self.text,self.attrs)
        return str(self.get_data())

def file_read(htmfile_path):
    htmfile=open(htmfile_path,"r")
    raw_text=htmfile.read()
    htmfile.close()

    return raw_text

def htm2list(htmfile_path):#最主要的函数，将一系列过程封装到这里了。
    parser=Parser()
    parser.feed(file_read(htmfile_path))

    #print(parser.get_result())
    _list=[ [block.get_data() for block in line] for line in parser.get_result() ]
    #print(_list)
    return _list

def print_analysed_data(htmfile_path):#彩蛋模式(单独运行而非被“调用”，即为彩蛋模式)用。
    parser=Parser()
    parser.feed(file_read(htmfile_path))

    for line in parser.get_result():
        for block in line:
            #print(block.analyse_style_attrs(block.attrs))
            print(block)
        print("newline")

if(__name__=="__main__"):
    #sys.exit(main())
    #print(htm2list("test3.htm"))
    cmd_parser=argparse.ArgumentParser(epilog="被你发现了呢~(｡･ω･｡)\n你想看看我能不能准确识别你通过编辑器生成的源文件吗？(￣3￣)",description="解析娘(・ω< )★")
    cmd_parser.add_argument("input_file")
    #print(cmd_parser.parse_args())

    input_file=cmd_parser.parse_args().input_file
    if(input_file):
        print("你在源文件里写了这些，你看看，我有说错什么吗？\n------------------------")
        print_analysed_data(input_file)
        print("\n-----------------------")
    else:
        print(cmd_parser.print_help())
