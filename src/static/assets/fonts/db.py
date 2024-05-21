import sys
from PIL import Image
import sqlite3
from pathlib import *

def main():
    db=Path.cwd() / "supported_chars.db"
    con=sqlite3.connect(str(db))
    cur=con.cursor()

    for font_id in range(1,5):
        cur.executemany("INSERT INTO font{0:n}_chars_size(name,width,height) VALUES(?,?,?)".format(font_id),get_data(font_id))

    con.commit()

def get_data(font_id):
    font_dir=Path.cwd() / "font-{0:n}".format(font_id) / "ms-orange"
    print(font_dir)

    cates=[font_dir / "letters" / "lower-case" ,font_dir / "letters" / "upper-case" ,font_dir / "numbers" ,font_dir / "symbols"]
    cates=[i for i in cates if(i.is_dir())]
    print(cates)

    chars=[]
    for i in cates:
        for j in [k for k in i.iterdir() if(k.is_file())]:
            chars.append(j)
    print(chars)

    data=[]
    for i in chars:
        line=[i.stem]
        img=Image.open(str(i))
        for j in img.size:
            line.append(j)
        data.append(line)

    print(data)
    return data

if(__name__=="__main__"):
    #sys.exit(main())
    sys.exit("批量写入数据用，用完即弃，请勿随意运行。")
