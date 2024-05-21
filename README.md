# MetalSlugFont-Word

## 简介

此仓库复刻于[VermeilChan/MetalSlugFontRebornWeb](https://github.com/VermeilChan/MetalSlugFontRebornWeb)。

本为群友之作。其支持生成单行单字体文字。甚是喜欢。随机萌生了自己“魔改”的想法，希望它能支持一次性输出多行字、多种字体。

复刻了群友的项目仓库后，经过约一周半时间，重写了所有代码，改出了0.1版。欢迎使用，也欢迎报告BUG，提出改进(至于能不能实现，得看我有没有精力了。“下次一定”吧233)，甚至再次复刻修改。

### 两版特性比对

个人认为这个有必要提一下：

#### 原版特性

1. 是网页应用程序，可以部署于网站。原作者自己也已经部署了一个，网站域名可前往原作者的仓库页面(见上)获取。若足下只有生成单行字的要求，或者不愿意搭建Python环境，可以考虑用原版。

#### 本分支版本特性

1. 是桌面图形应用程序。由纯Python写成，目前不打算发布打包版的Release。故想要运行，需要搭建好环境才能使用。

2. 采用`源文件-输出文件`模式。可以以类似MS Office Word的形式“可视化”地编辑源文件，再一键输出。

3. 允许调整输出图片的“页边距”“行距”“空行行高”

4. “顺便”支持了原版尚不能输出的字符。

<!-- 有彩蛋！ -->

## 环境要求

1. Python >= 3.10 因为代码中不少地方都用了match-case语句，这种语句是3.10版开始支持的。<s>或者……你可以自己将它们改成if-elif-else语句？</s>

2. PyQt5

3. Pillow

### 依赖安装

* 在`Ubuntu 24.04`上，可以直接利用`sudo apt install python3-pyqt5 python3-pil`命令安装依赖模块。

* 使用pip：(如有需要，需要先配置虚拟环境和下载源，再)运行命令`python3 -m pip install pyqt5 pillow #“python3”是Python解释器的名字，不同系统下会与此存在些许出入。`

## 运行方法

运行`src`目录下的`main.py`

![wyz-2015](src/static/assets/examples/sign.png)
