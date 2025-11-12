# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 18:23:58 2019
Created on Python3.6.8
@author:
    QQ:248411282
    Tel:13199701121
"""
# %% 开始
import numpy as np
from enum        import Enum
from dataclasses import dataclass
from liwancai.Functions.Formulae import *
#%% 基本定义
#class BStats(Enum):
#    '''
#    买卖级别划分,其核心目的是：将时空位置归类,用作统计分析;
#    通过统计分析归纳出在既定框架下的合理交易模式及规律方法。
#    ①你要明白你来自于哪里？你现在在哪？你将要去往何方？
#    ②你要明白你所处的环境是什么，你应该做和环境相匹配的事情。
#    '''
#    BSINIT= 0#白状态
#    BSZ001= 1#试盘买
#    BSZ002= 2#突破买
#    BSZ003= 3#上升买
#    BSZ004= 4#加速买
#    BSF002=-2#假突破
#class BSout(Enum):
#    '''
#    买卖行为标记
#    死叉区间买入BStats，金叉区间卖出10*BStats
#    核心逻辑:错配的需求推动行情发展。
#        在明确核心交易方向的首要前提下，
#        在多数人可能卖出的区间进货，
#        在多数人可能买入的区间卖货。
#    '''
#    BSINIT= 0#白状态
#    BSZ001= 10#试盘买
#    BSZ002= 20#突破买
#    BSZ003= 30#上升买
#    BSZ004= 40#加速买
#    BSF002=-20#假突破
#class LineStats(Enum):
#    '''
#    台阶状态划分
#    '''
#    LINIT  :int = 0###白状态
#    LineUP :int = 1###线涨
#    LineDW :int =-1###线跌
#    UPQS_L :int = 10##上涨趋势
#    DWQS_L :int =-10##下跌趋势
#    UPZD_L :int = 100#上涨震荡
#    DWZD_L :int =-100#下跌震荡
#    UPZD2L :int = 200#上涨双震
#    DWZD2L :int =-200#下跌双震
@dataclass
class CLSKV:
    '''
    数据类型CLSKV 
    值 v 
    序列:date_k
    
    '''
    value  :float=0   
    date_k :int  =0   
    
@dataclass
class line:
    '''
    台阶数据类型
    '''
    r  : float    = 0   ###红面积
    g  : float    = 0   ###绿面积
    date_k:int    = 0   ###台阶起点K的序列
    price :float  = 0   ###台阶价格
    ###------------------------------------------------------------------------
    #台阶高低点
    H : CLSKV     = CLSKV()#H值和key
    L : CLSKV     = CLSKV()#L值和key
    ###------------------------------------------------------------------------
    #动态有效防守位:
        #当前台阶与上一台阶的绝对差值为第一防守位
        #当前台阶与上二台阶的绝对差值是第二防守位
        #实时防守位:当且仅当入场时发现第一防守位已被打破时,才启动第二防守位
    guardl:float  = 0   ###实时防守位l
    guardh:float  = 0   ###实时防守位h
    ###------------------------------------------------------------------------
    guardU:float  = 0   ###第一防守位U涨方向
    guardD:float  = 0   ###第一防守位D跌方向
    guardUH:float = 0   ###第二防守位U涨方向
    guardDL:float = 0   ###第二防守位D涨方向
    ###------------------------------------------------------------------------
    BSout :int  = 0###买卖行为标记
    BStats:int  = 0###买卖级别的划分
    ###------------------------------------------------------------------------
@dataclass
class QSHL:
    '''趋势的高、低及各自序列'''
    H  : CLSKV     = CLSKV()#趋势区间的高
    L  : CLSKV     = CLSKV()#趋势区间的低
@dataclass
class ZDHL:
    '''震荡的高、低及各自序列'''
    H  : CLSKV     = CLSKV()#震荡区间的高
    L  : CLSKV     = CLSKV()#震荡区间的低
@dataclass
class QSUD:
    '''
    趋势结构
    趋势起点，趋势终点，台阶数量，台阶均差
    '''
    count :int        = 0   ###趋势台阶数量
    qsUDm :float      = 0   ###趋势台阶均差
    start : CLSKV     = CLSKV()##趋势台阶起点
    end   : CLSKV     = CLSKV()##趋势台阶终点
    
@dataclass
class Pivot:
    '''
    中枢 
    上沿 下沿
    '''
    pivotU :float     = 0   ###中枢上沿
    pivotD :float     = 0   ###中枢下沿
#%% 基本组件
class BSline:
    def __init__(self, bs, kline):
        '''初始化台阶结构线'''
        self.bs      :int   = bs###台阶BS标识：1 或 -1
        self.prices  :list  = []###台阶序列结点价格
        self.preline :float = kline.open###上一台阶价格
        self.lineUD1 :float = 0#一阶差
        self.lineUD2 :float = 0#二阶差
        ###--------------------------------------------------------------------
        self.div     :int   = 0#背驰||初始:0,临近背驰-金叉节点:1,临近背驰-追阳节点:2,趋势背驰:16
        self.double  :int   = 0#双震区间标识
        self.div_gs  :list  = [0,0]#趋势前后的震荡区间中绿区面积统计
        ###--------------------------------------------------------------------
        self.ZDk     :CLSKV = CLSKV()#震荡确认结点的K
        self.line    :list  = [line(),line(),line()]###基本台阶结构
        self.ZDHL    :list  = [ZDHL(),ZDHL(),ZDHL()]###震荡区间高低
        self.QSHL    :list  = [QSHL(),QSHL(),QSHL()]###趋势区间高低
        self.QSUD    :list  = [QSUD(),QSUD(),QSUD()]###趋势波段结构
        self.Pivot   :list  = [Pivot(),Pivot(),Pivot()]###中枢结构
        self.LStats  :list  = [0,0,0]###线的状态LineStats
        ###--------------------------------------------------------------------
    def resize(self):
        '''
        为保障运算效率，
        只维护最新三条序列元素。
        '''
        self.line   = self.line[-3:]
        self.QSUD   = self.QSUD[-3:]
        self.ZDHL   = self.ZDHL[-3:]
        self.QSHL   = self.QSHL[-3:]
        self.Pivot  = self.Pivot[-3:]
        self.div_gs = self.div_gs[-3:]
        self.LStats = self.LStats[-3:]
        self.prices = self.prices[-3:]
        ###--------------------------------------------------------------------
    def GetZDHL(self,kline):
        '''获取震荡区间的高低点'''
        ###--------------------------------------------------------------------
         ###对上个台阶结算时更新震荡,趋势区间的最高价最低价
        if abs(self.LStats[-1]) == 100:###上一台阶属于震荡100
            if abs(self.LStats[-2]) == 10:##上上台阶属于趋势#存在状态切换
                ###新增趋势后的第一个震荡区间用于承载新一轮震荡区间参数
                self.ZDHL.append(ZDHL(H=CLSKV(kline.high,kline.date_k),
                                      L=CLSKV(kline.low,kline.date_k)))
                
            ###更新震荡区间的高低值
            if  self.ZDHL[-1].H.value  < self.line[-1].H.value :###有新高
                self.ZDHL[-1].H.value  = self.line[-1].H.value  ###更新值
                self.ZDHL[-1].H.date_k = self.line[-1].H.date_k ###更新序列
                ###------------------------------------------------------------
            if  self.ZDHL[-1].L.value  > self.line[-1].L.value :###有新低
                self.ZDHL[-1].L.value  = self.line[-1].L.value  ###更新值
                self.ZDHL[-1].L.date_k = self.line[-1].L.date_k ###更新序列
                ###------------------------------------------------------------
    def GETQSHL(self,kline):
        '''获取趋势区间的高低点'''
        ###--------------------------------------------------------------------
        if abs(self.LStats[-1]) == 10: ###上一台阶属于趋势10
            if abs(self.LStats[-2]) == 100:##上上台阶属于震荡100#存在状态切换
                ###新增震荡后的第一个趋势区间用于承载新一趋势荡区间参数
                self.QSHL.append(QSHL(H=CLSKV(kline.high,kline.date_k),
                                      L=CLSKV(kline.low,kline.date_k)))
                self.ZDk = CLSKV()  #震荡确认节点清空##等待新的震荡来临
                self.Pivot.append(Pivot(pivotU=None,pivotD=None))###中枢新增
            ###更新趋势区间的高低值
            if  self.QSHL[-1].H.value  < self.line[-1].H.value :###有新高
                self.QSHL[-1].H.value  = self.line[-1].H.value  ###更新值
                self.QSHL[-1].H.date_k = self.line[-1].H.date_k ###更新序列
                ###------------------------------------------------------------
            if  self.QSHL[-1].L.value  > self.line[-1].L.value :###有新低
                self.QSHL[-1].L.value  = self.line[-1].L.value  ###更新值
                self.QSHL[-1].L.date_k = self.line[-1].L.date_k ###更新序列
                ###------------------------------------------------------------
        ###--------------------------------------------------------------------
    def GETdivs(self):
        '''获取背驰与中枢'''
        ###--------------------------------------------------------------------
         ###更新背驰
        if abs(self.LStats[-1]) == 100:  #上一台阶震荡,累加绿色面积
            self.div_gs[-1] += self.line[-1].g
        elif self.div_gs[-1] != 0:#上一条件不成立#上一台阶趋势,不累加,增加新的累计
            self.div = 0
            self.div_gs.append(0)
        ###--------------------------------------------------------------------
    def GETQSUD(self,kline,LinePrice):
        '''获取趋势台阶参数'''
        ###--------------------------------------------------------------------
         ###更新趋势波段起始点到结束点的台阶价格,台阶数量,平均台阶高度
        if abs(self.LStats[-1]) == 10:  #上一台阶处于趋势
            if abs(self.LStats[-2]) == 100:#上上台阶处于震荡
                ###第一个趋势台阶,更新起点终点及台阶高度
                qsUDm = (self.line[-1].price - self.line[-2].price)#台阶高度
                self.QSUD.append(QSUD(1,qsUDm,CLSKV(self.line[-2].price,kline.date_k),
                                              CLSKV(self.line[-1].price,kline.date_k)))
            else:###刷新台阶参数
                self.QSUD[-1].count       += 1
                self.QSUD[-1].end.value    = LinePrice
                self.QSUD[-1].end.date_k   = kline.date_k
                self.QSUD[-1].qsUDm        = (LinePrice-self.QSUD[-1].start.value)/self.QSUD[-1].count
        ###--------------------------------------------------------------------     
    def GETLineUD(self,LinePrice,kline):
        ###更新台阶参数
       self.lineUD1 = abs(LinePrice - self.line[-1].price) if self.line[-1].price != 0 else 0
       self.lineUD2 = max(abs(LinePrice - self.line[-2].price), self.lineUD1) if self.line[-2].price != 0 else self.lineUD1
       ###--------------------------------------------------------------------
       self.line.append(line(date_k=kline.date_k,price=LinePrice,
                       guardU  = (LinePrice + self.bs * self.lineUD1),
                       guardD  = (LinePrice - self.bs * self.lineUD1),
                       guardUH = (LinePrice + self.bs * self.lineUD2),
                       guardDL = (LinePrice - self.bs * self.lineUD2),
                       H=CLSKV(kline.high, kline.date_k),
                       L=CLSKV(kline.low , kline.date_k)))
       if len(self.line) < 2: return
       self.LStats.append(1 if self.bs * (self.line[-1].price - self.line[-2].price) > 0 else -1)
    def ProcessX(self,kline):
        '''台阶初始参数计算'''
        price = kline.close ###默认以收盘价为结点价格
        self.prices.append(price) ###添加结点价格到结点序列中
        if len(self.prices) < 3:return ###不足3个无法完成参数计算则跳出
        LinePrice = sum(self.prices[-3:]) / 3 ###最新台阶价
        ###--------------------------------------------------------------------
        ###请不要轻易改变↓的顺序
        self.GetZDHL(kline)            ##获取震荡区间的高低点
        self.GETQSHL(kline)            ##获取趋势区间的高低点
        self.GETdivs()                 ##获取背驰中枢
        self.GETQSUD(kline,LinePrice)  ##趋势台阶参数统计
        self.GETLineUD(LinePrice,kline)##更新台阶参数
        ###--------------------------------------------------------------------
    def Process(self, steps, kline, xline):
        '''台阶参数动态更新'''
        price = kline.close
        self.preline = (sum(self.prices[-2:]) + price) / 3#BS线预见价
        #======================================================================
        ###请不要轻易改变↓的顺序
        self.FlashHL(kline)             ###实时更新台阶高低
        self.FlashRG(steps)             ###实时更新红绿面积
        self.FlashQS(price)             ###实时更新趋势状态
        self.FlashZD(kline,steps,xline) ###实时更新震荡状态
        self.FlashGD(price)             ###实时更新防守位
        self.FlashPV()                  ###实时更新中枢
        self.FlashDV(steps)             ###实时更新背驰状态
        self.FlashBS(steps)             ###实时更新买卖级别及状态
        #======================================================================
    def FlashHL(self,kline):
        #======================================================================
        #台阶最高价,最低价
        if kline.high > self.line[-1].H.value :self.line[-1].H=CLSKV(kline.high,kline.date_k)
        if kline.low  < self.line[-1].L.value :self.line[-1].L=CLSKV(kline.low ,kline.date_k)
    def FlashRG(self,steps):
        #======================================================================
        #台阶红绿面积更新
        if self.bs * steps.Vols > 0: self.line[-1].r = abs(steps.Vols)
        if self.bs * steps.Vols < 0: self.line[-1].g = abs(steps.Vols)
    def FlashQS(self,price):
        #======================================================================
        #台阶趋势震荡状态更新
        b = self.bs * (price - self.line[-1].price)
        if len(self.LStats)  <  1 : return
        if self.LStats[-1]  ==  1 and b >= 0:   self.LStats[-1] =  10
        if self.LStats[-1]  == -1 and b <= 0:   self.LStats[-1] = -10
        if (self.LStats[-1] ==  1 or self.LStats[-1] ==  10) and b < 0:   self.LStats[-1] =  100
        if (self.LStats[-1] == -1 or self.LStats[-1] == -10) and b > 0:   self.LStats[-1] = -100
    def FlashZD(self,kline,steps,xline):
        #======================================================================
        #更新震荡标识
        if (abs(self.LStats[-2]) == 10) and (abs(self.LStats[-1]) == 100) and (self.ZDk.value == 0):
            self.ZDk =CLSKV(kline.close, kline.date_k)###震荡开始K的收盘价及K线序列
        #======================================================================
        #双震区间#同向 绿区红区 价格反转
        Fuck_stats=(self.LStats[-1] * xline.LStats[-1] < 0)     #区间状态相反
        Fuck_Vols =(self.bs * self.LStats[-1] * steps.Vols < 0 )#成本区间状态相反
        Fuck_price=(self.bs * (self.line[-1].price - xline.line[-1].price) <0)#成本价格相背
        self.double = 1 if Fuck_stats and Fuck_Vols and Fuck_price  else 0 
    def FlashGD(self,price):
        #======================================================================
        #动态有效防守位:
        #当前台阶与上一台阶的绝对差值为第一防守位
        #当前台阶与上二台阶的绝对差值是第二防守位
        #当且仅当入场时发现第一防守位已被打破时,才启动第二防守位
        if self.bs * (price - self.line[-1].guardl) <= 0: self.line[-1].guardl = self.line[-1].guardDL
        if self.bs * (price - self.line[-1].guardh) >= 0: self.line[-1].guardh = self.line[-1].guardUH
        #======================================================================
    def FlashPV(self):
        #动态中枢
        if (abs(self.LStats[-1]) == 100) and (self.line[-1].price != abs(self.QSUD[-1].qsUDm)):
            self.Pivot[-1].pivotU = self.line[-1].price + self.bs *  abs(self.QSUD[-1].qsUDm)
            self.Pivot[-1].pivotD = self.line[-1].price - self.bs *  abs(self.QSUD[-1].qsUDm)
    def FlashDV(self,steps):
        #======================================================================
        #趋势背驰&临近背驰
        #======================================================================
        if len(self.LStats) < 2: return
        #临近背驰判断 当前状态是震荡,相邻状态是震荡,绿面积已经计算完成,判断背驰
        if abs(self.LStats[-1]) == 100 and abs(self.LStats[-2]) == 100:  #临近背驰判断
            if self.line[-1].g < self.line[-2].g and self.bs * steps.Vols > 0:  #绿面积减小，发生临近背驰
                self.div |= 1  #发生临近背驰——金叉节点
            if self.line[-1].r > self.line[-2].r:  #当前最新累加红面积≥上一台阶红面积
                self.div |= 2  #发生临近背驰——追阳节点
        #======================================================================
        if self.bs * steps.Vols < 0: self.div &= ~3  
        #退出临近背驰{临近背驰的有效区间仅为当下红面积区间,至于接下来走出的趋势还是震荡都需要后者动态判断}
        #======================================================================
        if len(self.div_gs) < 2: return
        #趋势背驰判断 当下属于震荡区间,且相邻震荡数量大于等于一,计算相邻所有震荡的绿面积与当前的绿面积之和,与趋势前的绿面积比较
        #======================================================================
        #当只有两个震荡时
        if abs(self.LStats[-1]) == 100 and abs(self.LStats[-2]) == 100 \
            and abs(self.LStats[-3]) != 100 and self.bs * steps.Vols > 0 and \
            self.div_gs[-1] + self.line[-1].g < self.div_gs[-2]:
            self.div |= 16  #发生趋势背驰
        #======================================================================
        #当有三个及以上震荡时
        if abs(self.LStats[-1]) == 100 and abs(self.LStats[-2]) == 100 \
            and abs( self.LStats[-3]) == 100 and self.div_gs[-1] + self.line[-1].g < self.div_gs[-2]:
            self.div |= 16  #发生趋势背驰
        #======================================================================
        #趋势区间不计入背驰↓
        if (self.div_gs[-1] + self.line[-1].g > self.div_gs[-2]) | abs(self.LStats[-1]) != 100:  
            self.div &= ~16  #退出趋势背驰{当面积背驰面积条件由满足变成不满足时退出}
    def FlashBS(self,steps):
        #======================================================================
        #级别买区间状态标识  {0:初始态 1:试买 2:一买  3:二买  4:三买}
        ###0#白状态 1#试盘买2#突破买3#上升买4#加速买-2#假突破
        if abs(self.LStats[-2]) == 100 and abs(self.LStats[-1]) == 100:
            self.line[-1].BStats = 1   #震荡+震荡=试买
        if self.line[-2].BStats == 1 and self.LStats[-1] == 10:
            self.line[-1].BStats = 2   #试买+上涨=一买
        if self.line[-2].BStats == 1 and self.LStats[-1] == -10:
            self.line[-1].BStats = -2  #试买+下跌=一卖
        if self.line[-2].BStats == 2 and self.LStats[-1] == 10:
            self.line[-1].BStats = 3   #一买+上涨=二买
        if self.line[-2].BStats == 3 and self.LStats[-1] == 10:
            self.line[-1].BStats = 3   #二买+上涨=二买
        if self.line[-2].BStats == 3 and abs(self.LStats[-1]) == 100 and -self.bs * steps.rgcount <= 3:
            self.line[-1].BStats = 4   #二买+震荡(≤3)=三买
        if self.line[-2].BStats == 4 and self.LStats[-1] == 10:
            self.line[-1].BStats = 2   #三买+上涨=一买
        if self.line[-2].BStats == 4 and abs(self.LStats[-1]) == 100:
            self.line[-1].BStats = 1   #三买+震荡=试买
        if self.line[-2].BStats == 4 and self.LStats[-1] == -10:
            self.line[-1].BStats = -2  #三买+下跌=一卖
        #======================================================================
        #买卖行为标记 #死叉区间买入BStats，金叉区间卖出 10*BStats
        self.line[-1].BSout = 10 * self.line[-1].BStats if self.bs * steps.Vols > 0 else self.line[-1].BStats
        #======================================================================
 
#%% 标准结构
class MACD_BS:
    def __init__(self, kline,mark=0):
        self.mark = mark
        self.rgcount,self.vol, self.Vols,self.dif, self.dea, self.macd= 0,0,0,0,0,0
        self.Sline = BSline( 1,  kline)   # 卖出成本线
        self.Bline = BSline(-1,  kline)   # 买入成本线
        self.MACD  = MACD()###结点源自于MACD
    def input(self, kline, promotion=1, e12=12, e26=26, e9=9):
        price    = kline.close
        self.vol = kline.volume
        ###--------------------------------------------------------------------
        self.MACD.input(price,promotion, e12, e26, e9)
        self.dif = self.MACD.dif
        self.dea = self.MACD.dea
        ###--------------------------------------------------------------------
        # 区间面积统计,节点序列生成
        if self.MACD.macd < 0:   # 死叉区间
            if self.rgcount <= 0:  # 死叉
                self.Vols -= self.vol
                self.rgcount -= 1
            else:
                self.rgcount = -1
                self.Vols = -self.vol
                self.Sline.resize()
                self.Sline.ProcessX(kline)
        else:                    # 金叉区间
            if self.rgcount >= 0:  # 金叉
                self.Vols += self.vol
                self.rgcount += 1
            else:
                self.rgcount = 1
                self.Vols = self.vol
                self.Bline.resize()
                self.Bline.ProcessX(kline)
        ###--------------------------------------------------------------------
        self.Sline.Process(self, kline, self.Bline)
        self.Bline.Process(self, kline, self.Sline)
        ###--------------------------------------------------------------------
# %% 终结


