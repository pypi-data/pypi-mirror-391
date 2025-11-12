# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 17:32:43 2019
Created on Python3.6.8
@author:
    liwancai
    QQ:248411282
"""
import numpy as np
import matplotlib.pyplot            as plt
import mplfinance.original_flavor   as mpf
import matplotlib.gridspec          as gridspec
from liwancai.Functions.DirsFile import Mkdir
from liwancai.Functions.Formulae import RColor
# ==============================================================================
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'
plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 这两行需要手动设置
# ==============================================================================
def PltTxt(X, Y, TXT, color="magenta", fontsize=18.8,
           verticalalignment='center', horizontalalignment='center',
           style='normal', family='SimHei', weight='heavy',
           bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='yellow', lw=2, alpha=0.7)):
    plt.text(X, Y, TXT, color=color, fontsize=fontsize, verticalalignment=verticalalignment,
             horizontalalignment=horizontalalignment, style=style, family=family, weight=weight, bbox=bbox)
# ==============================================================================
def PltTable(df, loc="center", cellLoc="center", fontsize=30,**arges):
    plt.table(cellText=df.values, fontsize=fontsize, colLabels=df.columns, 
              colColours=RColor(len(df.columns)), loc=loc,cellLoc=cellLoc,**arges)
# ==============================================================================
def PltKline(Subplot,df,arge=['kid','open','close','high','low']):
    mpf.candlestick_ochl(Subplot,quotes=df[arge].values,width=0.5,colorup='r', colordown='g',alpha=0.9)
# ==============================================================================
def PltBar(X, Y, color="magenta", label=None):
    """
    一个创建条形图的函数。

    参数:
        X (array-like): 条形图的x坐标。
        Y (array-like): 条形图的高度。
        color (str, optional): 条形图的颜色。默认为"magenta"。
        label (str, optional): 图例的标签。默认为None。

    返回:
        matplotlib.container.BarContainer: 表示条形图的BarContainer对象。
    """
    return plt.bar(X, Y, label=label, facecolor=color)
# ==============================================================================
def PltPoint(X, Y, color="magenta", linewidth=1, label=None):
    """
    一个函数，用于在图表上绘制指定的X和Y坐标的单个点。

    参数:
        X (类数组): 点的X坐标。
        Y (类数组): 点的Y坐标。
        color (str, 可选): 绘制点的颜色。默认为"magenta"。
        linewidth (int, 可选): 线的宽度。默认为1。
        label (str, 可选): 点的标签。默认为None。

    返回:
        list: 代表绘制数据的Line2D对象列表。
    """
    return plt.plot(X, Y, 'r.', color=color, linewidth=linewidth, label=label)
# ==============================================================================
def PltLine(X, Y, TYPE="-.", color="red", linewidth=1, label=None):
    """
    一个函数，用指定的颜色、线型、线宽和透明度在给定的子图上生成网格。

    参数:
    subplts : object
        将生成网格的子图。
    color : str, 可选
        网格线的颜色（默认为'r'）。
    linestyle : str, 可选
        网格线的样式（默认为'--'）。
    linewidth : int, 可选
        网格线的宽度（默认为1）。
    alpha : float, 可选
        网格线的透明度（默认为0.3）。
    """
    return plt.plot(X, Y, TYPE, color=color, linewidth=linewidth, label=label)
# ==============================================================================
def Grde(subplts, color='r', linestyle='--', linewidth=1, alpha=0.3):
    subplts.grid(color=color, linestyle=linestyle, linewidth=linewidth, alpha=alpha)
# ==============================================================================
def NoneXY():
    '''移除绘图中x和y轴的刻度标记。'''
    plt.xticks([])
    plt.yticks([])
# ==============================================================================
def AxisXY(X, label=[], NUM=6, color="red", fontsize=18.8, xl=True, spaceall=100):
    '''标注X轴xl=True  Y轴xl=False'''
    if len(label) > 0:
        X = np.linspace(min(X), max(X), len(label))
    else:
        X = np.linspace(min(X), max(X), spaceall)
    NUM = (len(X) // NUM) if len(X) > NUM else 1
    label = label[::NUM] if len(label) > 0 else None
    if xl:
        plt.xticks(X[::NUM], labels=label, color=color, fontsize=fontsize)
    else:
        plt.yticks(X[::NUM], labels=label, color=color, fontsize=fontsize)
# ==============================================================================
class PltFig:
    def __init__(self,图像标识=None, 
                行=3, 列=2, 宽=60, 长=60, 
                分辨率=100, 背景颜色="white",
                边框颜色="black", 显示边框=False,
                PATH='./Datas/IMDatas/'):
        """
        初始化PltFig对象

        参数:
        图像标识: 图像的标识，可选
        行: 子图的行数，默认为3
        列: 子图的列数，默认为2
        宽: 图像的宽度，默认为60
        长: 图像的长度，默认为60
        分辨率: 图像的分辨率，默认为100
        背景颜色: 图像的背景颜色，默认为"white"
        边框颜色: 图像的边框颜色，默认为"black"
        显示边框: 是否显示图像边框，默认为False
        PATH: 存储图像的路径，默认为'./Datas/IMDatas/'
        """
        self.PATH = PATH
        Mkdir(self.PATH)
        self.fig = plt.figure(num=图像标识, figsize=(长, 宽), dpi=分辨率, facecolor=背景颜色, edgecolor=边框颜色, frameon=显示边框)
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.1, hspace=0.1)
        self.gs = gridspec.GridSpec(行, 列)
    def Addsubplot(self, 行=2, 列=3, 序列=1):
        """
        添加子图到图像中

        参数:
        行: 子图的行数，默认为2
        列: 子图的列数，默认为3
        序列: 子图的序列号，默认为1

        返回:
        添加的子图对象
        """
        return self.fig.add_subplot(行, 列, 序列)
    def SaveFig(self, filename):
        """
        保存图像为PNG格式

        参数:
        filename: 保存的图像文件名
        """
        self.fig.savefig(self.PATH + filename + '.png')
        plt.cla()
        plt.clf()
        plt.close()
    def Pltsubplot(self, y0=0, y1=2, x0=0, x1=2, facecolor="lightgray"):
        """
        创建独立的子图

        参数:
        y0: 子图的起始行，默认为0
        y1: 子图的结束行，默认为2
        x0: 子图的起始列，默认为0
        x1: 子图的结束列，默认为2
        facecolor: 子图的背景颜色，默认为"lightgray"

        返回:
        创建的子图对象
        """
      
 
        return   plt.subplot(self.gs[y0:y1, x0:x1], facecolor=facecolor)


if __name__ == "__main__":
    ### 案例数据
    X = np.linspace(0, 10, 100)
    ### 创建画布 
    fig = PltFig(图像标识="001", 行=3, 列=2, 宽=60, 长=60, 分辨率=120, 背景颜色="white", 边框颜色="black", 显示边框=False, PATH='./Datas/IMDatas/')
    Pltsubplot1 = fig.Pltsubplot(y0=0, y1=2, x0=0, x1=2)
    ### fig_1
    fig_1=fig.Addsubplot(行=3,列=2,序列=1)
    PltLine(X, X * 2, TYPE="-.", color="red", linewidth=1, label=None)
    PltTxt(4, 4, "测试", color="magenta", fontsize=18.8)
    PltBar(2, 4, color="magenta", label="None")
    PltPoint(4, 16, color="magenta", linewidth=1, label=None)
    NoneXY()
    AxisXY(X, label=[], NUM=6, color="red", fontsize=18.8, xl=True)
    AxisXY(X * 2, label=[], NUM=12, color="red", fontsize=18.8, xl=False)
    Grde(fig_1, color='r', linestyle='--', linewidth=1, alpha=0.3)
    ax1 = fig_1.twinx()
    PltLine(X, X ** 2, TYPE="-.", color="blue", linewidth=1, label=None)
    AxisXY(X ** 2, label=[], NUM=36, color="blue", fontsize=18.8, xl=False)
    ### fig_2
    Pltsubplot2 = fig.Pltsubplot(y0=2, y1=3, x0=1, x1=2)
    fig_2=fig.Addsubplot(行=3,列=2,序列=2)
    ### 保存图片
    fig.SaveFig("gggg")
    plt.legend()
    plt.title("title")
    plt.savefig("filepath"+"title"+'.png')
    plt.cla()
    plt.clf()
    plt.close()
