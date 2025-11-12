# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 20:07:00 2019
Created on Python3.6.8
@author:liwancai
    QQ:248411282
    Tel:13199701121
"""
import numpy                        as np
import pandas                       as pd
from liwancai.Functions.LOG        import log
from tqdm                           import tqdm
from multiprocessing                import Pool
from liwancai.Functions.DirsFile   import Mkdir
from pandas                         import Series
from prettytable                    import PrettyTable
from concurrent.futures             import ThreadPoolExecutor
from datetime                       import datetime,timedelta
import requests,re,copy,prettytable,random,multiprocessing,time
#//////////////////////////////////////////////////////////////////////////////
def NewCode(code: str) -> str:
    if code.startswith("0") or code.startswith("3") :
        return code + ".SZ"
    elif code.startswith("6") or code.startswith("5") :
        return code + ".SH"
    else:
        return code + ".BJ"
# %% 公式
class AUMA:
    '''自由均线'''
    def __init__(self,Length=2000, mark=0):
        self.mark,self.Length=mark,Length
        self.ma, self.malist = 0, []
    def input(self, price, e0=5, promotion=1):
        if e0<1:e0=1
        self.malist.append(price)
        self.ma = sum(self.malist[-promotion * e0:]) / len(self.malist[-promotion * e0:])
        self.malist = self.malist[-self.Length:]
#//////////////////////////////////////////////////////////////////////////////
class MAFS:
    """日内自由均线"""
    def __init__(self,Length=2000, mark=0):
        self.AUMAA=AUMA(Length=Length, mark=0)
        self.AUMAB=AUMA(Length=Length, mark=1)
        self.AUMAC=AUMA(Length=Length, mark=2)
    def input(self,price , N=1 , ks1day=345 , limitN=5 ):
        halfD = int(0.5 * ks1day)
        lastN = ks1day - N
        halfN = abs(halfD -N)
        lastH = halfD - halfN
        
        N0 = min(lastH, halfN)
        N1 = max(lastH, halfN)
        N2 = max(lastN, N    )
        if N0<limitN:N0 = limitN
        self.AUMAA.input(price, N0,1)
        self.AUMAB.input(price, N1,1)
        self.AUMAC.input(price, N2,1)
#//////////////////////////////////////////////////////////////////////////////
class MA:
    def __init__(self, mark=0):
        self.mark = mark
        self.ma, self.malist = 0, []
    def input(self, price, e0=5, promotion=1):
        if e0<1:e0=1
        self.malist.append(price)
        self.malist = self.malist[-promotion * e0:]
        self.ma = sum(self.malist) / len(self.malist)
#//////////////////////////////////////////////////////////////////////////////
class EMA:
    def __init__(self, mark=0):
        self.mark = mark
        self.ema = 0
    def input(self, price, e0=12, promotion=1):
        if e0<1:e0=1
        self.ema = (price * 2 + self.ema * (promotion * e0 - 1)) / (promotion * e0 + 1)
#//////////////////////////////////////////////////////////////////////////////
class VHSL:
    '''周转率'''
    def __init__(self, mark=0):
        self.hsl ,self.REFVol = 0 ,0
        self.Vols,self.VolXs  = [],[]
    def input(self, vol, e0=21, promotion=1):
        if e0<1:e0=1
        self.Vols.append(vol)
        self.VolXs.append(vol-self.REFVol)
        self.Vols = self.Vols[-e0*promotion:]
        self.VolXs= self.VolXs[-e0*promotion:]
        self.hsl = 100*vol /(sum(self.Vols)+sum(self.VolXs))
        self.REFVol =vol
class BIAS:
    def __init__(self, mark=0):
        self.bias = 0
        self.EMA  = EMA()
        self.Mbias= MA()
    def input(self, price, e0=12, promotion=1,em=5):
        self.EMA.input(price, e0, promotion)
        self.bias = 100 * (price - self.EMA.ema) / self.EMA.ema if self.EMA.ema !=0 else 0
        self.Mbias.input(self.bias,em,promotion)
#//////////////////////////////////////////////////////////////////////////////
class DifferB:
    def __init__(self,mark=0):
        self.mark = mark
        self.REFP ,self.REFD,self.difB,self.REFF,self.difdif= None,None,0,None,0
    def input(self,price,per):
        '''
        计算X增量百分比的增量的倍数
        XV:=100*(V-REF(V,1))/V;
        YV:ABS(XV-REF(XV,1)),STICK;
        IF(YV/REF(YV,1)>6,YV,0),VOLSTICK;
        '''
        if not self.REFP:self.REFP=price
        difper=100*(price-self.REFP)/self.REFP
        if not self.REFD:self.REFD=difper
        self.difdif=abs(difper-self.REFD)/self.REFD
        if not self.REFF:self.REFF=self.difdif
        self.difB=self.difdif if (self.difdif/self.REFF)>per  else 0
        self.REFP,self.REFD,self.REFF=price,difper,self.difdif
#//////////////////////////////////////////////////////////////////////////////
class DubEMA:  # 双均线
    def __init__(self, mark=0):
        self.mark = mark
        self.EMA0 = EMA()
        self.EMA1 = EMA()
    def input(self, gc, promotion=1, e0=12, e1=1440):
        self.EMA0.input(gc, e0, promotion)
        self.EMA1.input(gc, e1, promotion)
#//////////////////////////////////////////////////////////////////////////////
class SMA:
    def __init__(self, mark=0):
        self.mark = mark
        self.sma = 0
    def input(self, price, N=21, M=3, promotion=1):
        if N<1:N=1
        self.sma = (price *M + self.sma * (N * promotion - M)) / (N*promotion) if (N*promotion)!=0 else 0
#//////////////////////////////////////////////////////////////////////////////
class Boll:
    '''BOLL'''
    def __init__(self, mark=0):
        self.mark = mark
        self.EMA  = EMA()
        self.alist,self.BSP=[],0
        self.boll ,self.bollH ,self.bollL ,self.stdvalue= 0,0,0,0
    def input(self, price,N=12,G=2, promotion=1):
        self.EMA.input(price,N,promotion)
        self.boll=self.EMA.ema
        self.alist.append(price)
        self.alist=self.alist[-promotion*N:]  
        self.stdvalue=G*(np.std(np.array(self.alist)))
        self.bollH = self.boll + self.stdvalue #布林带高
        self.bollL = self.boll - self.stdvalue #布林带低
        HP , LP = abs(price-self.bollH) , abs(price-self.bollL)
        self.BSP=max(HP,LP)/min(HP,LP) if min(HP,LP)!=0 else 0 #BS空间比值 
#//////////////////////////////////////////////////////////////////////////////
class HLV:#定周期(默认5日)最高价最低价
    def __init__(self, mark=0):
        self.mark = mark
        self.H, self.L, self.argelist = 0, 0, []
    def input(self, price, arge=5):
        self.argelist.append(price)
        self.argelist = self.argelist[-2 * arge:]
        self.H = max(self.argelist[-arge:])#高
        self.L = min(self.argelist[-arge:])#低
#//////////////////////////////////////////////////////////////////////////////
class RSI:
    def __init__(self, mark=0):
        self.mark = mark
        self.SMA0, self.SMA1, self.rsi, self.REFC = SMA(), SMA(), 0, 1

    def input(self, price, N=6, M=1, promotion=1):
        self.SMA0.input(max(price - self.REFC, 0), N, M, promotion)
        self.SMA1.input(abs(price - self.REFC), N, M, promotion)
        self.rsi = (self.SMA0.sma / self.SMA1.sma * 100) if self.SMA1.sma else 0
        self.REFC = price
#//////////////////////////////////////////////////////////////////////////////
class CCL:
    '''
    持仓量
    '''
    def __init__(self, mark=0):
        self.mark = mark
        self.REFC, self.REFOI, self.result = 1, 1, ''
    def input(self, price, oi):
        self.OI = oi
        self.oiX = self.OI - self.REFOI
        self.result = '空头增仓' if (self.oiX > 0 and price < self.REFC) else self.result
        self.result = '多头增仓' if (self.oiX > 0 and price >=self.REFC) else self.result
        self.result = '多头减仓' if (self.oiX < 0 and price < self.REFC) else self.result
        self.result = '空头减仓' if (self.oiX < 0 and price >=self.REFC) else self.result
        self.REFC, self.REFOI = price, oi
#//////////////////////////////////////////////////////////////////////////////
class CCLX:
    '''
    持仓净值
    OIX:=OPI-REF(OPI,1);
    CX:=C-REF(C,1);
    UP:=IF(CX>0 AND OIX>0 , OIX,0);//多开
    DW:=IF(CX<0 AND OIX>0 ,-OIX,0);//空开
    UPX:=IF(CX<0 AND OIX<=0 ,OIX,0);//多平
    DWX:=IF(CX>0 AND OIX<=0 ,-OIX,0);//空平
    净买:SUM(UP+UPX,30);//持仓量净买
    净卖:SUM(DW+DWX,30);//持仓量净卖
    净买卖:SUM(UP+UPX+DW+DWX,30);////多空持仓量净值
    '''
    def __init__(self,mark=0):
        self.mark = mark
        self.REFC, self.REFOI= 1, 1
        self.NoB,self.NoS,self.NoBS=MA(),MA(),MA()
    def input(self,kline,Bnum=30,Snum=30,BSnum=30,promotion=1):
        CX  =kline.close-self.REFC
        OIX =kline.oi  -self.REFOI
        UP = OIX  if CX>0 and OIX>0 else 0  ###多开
        DW =-OIX  if CX<0 and OIX>0 else 0  ###空开
        UPX= OIX  if CX<0 and OIX<=0 else 0 ###多平
        DWX=-OIX  if CX>0 and OIX<=0 else 0 ###空平
        self.NoB.input(UP+UPX,Bnum,promotion)#N周期的持仓量净买
        self.NoS.input(DW+DWX,Snum,promotion)#N周期的持仓量净卖
        self.NoBS.input(UP+UPX+DW+DWX,BSnum,promotion)#N周期的多空持仓量净值
        self.REFC, self.REFOI = kline.close, kline.oi
#//////////////////////////////////////////////////////////////////////////////
class SKDJ:
    '''
    6:2 12:7 21:7 45:15 120:40 210:70 450:150 1200:400
    '''
    def __init__(self, mark=0):
        self.mark = mark
        self.H = HLV()
        self.L = HLV()
        self.EMARSV = EMA()
        self.EMAK   = EMA()
        self.EMAD   = EMA()
        
        self.K   ,self.D    = 1,1
        self.REFK,self.REFD = 1,1
        self.scoreUP,self.scoreDW = 0,0
        self.fmstatu,self.statu,self.updwQ,self.Aline= 0,0,0,None
        self.JXSX,self.BaseP,self.FreeP,self.SumP = 1,CLS({"UP":0,"DW":0}),CLS({"UP":0,"DW":0}),CLS({"UP":0,"DW":0})
    def input(self, kline, N=9, M=3, promotion=1,HML=[75,50,25],BaseList = [0.125,0.25,0.375,0.5]):
        '''
        金叉死叉位置为初值,曲线区间计算动态值，两值相加是能量
        
        '''
        if not self.Aline:self.Aline=kline.open
        self.H.input(kline.high, N * promotion)
        self.L.input(kline.low , N * promotion)
        RSV = ((kline.close - self.L.L) / (self.H.H - self.L.L) * 100) if self.H.H != self.L.L else 0
        self.EMARSV.input(RSV, M, promotion)
        self.EMAK.input(self.EMARSV.ema, M, promotion)
        self.K = self.EMAK.ema
        self.EMAD.input(self.K, M, promotion)
        self.D = self.EMAD.ema
        ###====================================================================
        self.JXSXMark()#交叉标记
        self.Source(kline,HML)  #源头分析
        self.SplitKD() #二元分离
        ###====================================================================
        self.Score()#多空评分
        self.MarkP(BaseList)#浮动能量
        self.REFK,self.REFD = self.K, self.D
        ###====================================================================
    def MarkP(self,BaseList = [12.5,25,37.5,50]):
        '''浮动能量'''
        self.FreeP.UP ,self.FreeP.DW =  (100-self.K)/2,self.K/2
        if self.JXSX== 1 :self.BaseP.UP = BaseList[self.statu-1]#金叉结点
        if self.JXSX==-1 :self.BaseP.DW = BaseList[-1*self.statu]#死叉结点
        self.SumP.UP  ,self.SumP.DW  =  self.BaseP.UP+self.FreeP.UP,self.BaseP.DW+self.FreeP.DW
    def Source(self,kline,HML):
        '''源头分析'''
        ###====================================================================
        if (self.K>=HML[1]):
            self.statu=2#50上
            #如果KD都在75之上则定义高
            if (self.K>HML[0])or(self.D>HML[0]):
                self.fmstatu,self.statu= 1,1#上#四分位
                if kline.high>self.Aline:self.Aline=kline.high#记录高点源头
        else:
            self.statu=3#50下
            #如果KD都在25之下则定义低
            if (self.K<HML[-1])or(self.D<HML[-1]):
                self.fmstatu,self.statu=-1,4#下#四分位
                if kline.low<self.Aline:self.Aline=kline.low #记录低点源头
        ###====================================================================
    def SplitKD(self):
        '''二元分离'''
        if   self.K>self.D:self.updwQ= 1
        elif self.K<self.D:self.updwQ=-1
        else:self.updwQ = 0
        
    def JXSXMark(self):
        '''金叉死叉标记累计'''
        if   CROSX(self.K,self.D,self.REFK,self.REFD)==1:self.JXSX =  1#金叉
        elif CROSX(self.D,self.K,self.REFD,self.REFK)==1:self.JXSX = -1#死叉
        else:self.JXSX+=(self.JXSX)/(abs(self.JXSX))#累计金叉死叉
        ###====================================================================
    def Score(self):
        ###级别多空评分1-8 ±1
        FS0=self.statu*2 
        if   self.updwQ<0:FS0+=self.updwQ#逆多
        if self.fmstatu<0:FS0-=self.fmstatu#底部+1
        self.scoreUP=FS0#做多分
        ###====================================================================
        FS1=(5-self.statu)*2 
        if   self.updwQ>0:FS1-=self.updwQ#逆空
        if self.fmstatu>0:FS1+=self.fmstatu#顶部+1
        self.scoreDW=FS1#做空分
        ###====================================================================


#//////////////////////////////////////////////////////////////////////////////
class KDJ:
    def __init__(self, mark=0):
        self.mark = mark
        self.H = HLV()
        self.L = HLV()
        self.EMAK = EMA()
        self.EMAD = EMA()
        self.K, self.D, self.J = 1, 1, 1

    def input(self, kline, N=9, M=3, promotion=1):
        self.H.input(kline.high, N * promotion)
        self.L.input(kline.low, N * promotion)
        RSV = ((kline.close - self.L.L) / (self.H.H - self.L.L) * 100) if self.H.H != self.L.L else 0
        self.EMAK.input(RSV, M, promotion)
        self.K = self.EMAK.ema
        self.EMAD.input(self.K, M, promotion)
        self.D = self.EMAD.ema
        self.J = 3 * self.K - 2 * self.D
#//////////////////////////////////////////////////////////////////////////////
class RNV:  #
    '''有效成交量'''
    def __init__(self, mark=0):
        self.mark = mark
        self.REFC, self.REFV, self.rnv = 1, 1, 1
    def input(self, kline):
        self.CHGP = (kline.close / self.REFC - 1)
        self.rnv = self.CHGP * abs(
            kline.close * kline.volume - self.REFC * self.REFV) if kline.close == kline.open else self.CHGP * abs(
            kline.close * kline.volume - kline.open * kline.volume)
        self.REFC, self.REFV = kline.close, kline.volume
#//////////////////////////////////////////////////////////////////////////////
class RSMA:
    '''相对强弱MA'''
    def __init__(self, mark=0):
        self.mark = mark
        self.SMA0, self.SMA1, self.MA12, self.rsi = SMA(), SMA(), MA(), 0
    def input(self, price, N=25, M=1, promotion=1, e0=12):
        self.MA12.input(price, e0, promotion)
        self.SMA0.input(max(price - self.MA12.ma, 0), N, M, promotion)
        self.SMA1.input(abs(price - self.MA12.ma), N, M, promotion)
        self.rsi = (100* self.SMA0.sma / self.SMA1.sma ) if self.SMA1.sma else 0
#//////////////////////////////////////////////////////////////////////////////
class TD_N9:
    '''神奇九转'''
    def __init__(self):
        self.TDB,self.TDS,self.REFTDB,self.REFTDS=0,0,0,0
        self.Hs,self.Ls,self.Cs=[],[],[]
    def input(self,kline):
        ###记录高低数据↓
        self.Hs.append(kline.high)
        self.Ls.append(kline.low )
        self.Cs.append(kline.close)
        if len(self.Cs)<10:return 
        ###当前TD结构状态↓
        ###//////////////////////////////////////////////////////////////////
        ###序列1~7
        if   kline.close<self.Cs[-5]:self.TDB+=1
        ###序列8~9
        elif (self.REFTDB>=7)&(kline.low <self.Ls[-(self.REFTDB-5)])&(kline.low <self.Ls[-(self.REFTDB-4)]):self.TDB+=1
        else:self.TDB=0
        ###//////////////////////////////////////////////////////////////////
        ###序列1~7
        if kline.close>self.Cs[-5]:self.TDS+=1
        ###序列8~9
        elif (self.REFTDS>=7)&(kline.high>self.Hs[-(self.REFTDS-5)])&(kline.high<self.Hs[-(self.REFTDS-4)]):self.TDS+=1
        else:self.TDS=0
        ###//////////////////////////////////////////////////////////////////
        if self.TDB>9:self.TDB=9
        if self.TDS>9:self.TDS=9
        self.REFTDB,self.REFTDS=self.TDB,self.TDS
        self.Hs,self.Ls,self.Cs=self.Hs[-21:],self.Ls[-21:],self.Cs[-21:]
        ###//////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////
class ATR:  #
    '''ATR+策略'''

    def __init__(self, mark=0):
        self.mark = mark
        self.MTR, self.HBS, self.LBS, self.atr, self.Matr, self.REFHL = 0, 0, 0, 0, MA(), [1, ] * 4
        self.HH, self.LL = HLV(), HLV()
    def input(self, kline, promotion=1, M0=20, arge=21, N=2):  # 回撤N个ATR离场
        self.MTR = max(kline.high - kline.low, abs(self.REFHL[2] - kline.high), abs(self.REFHL[2] - kline.low))
        self.Matr.input(self.MTR, M0, promotion)  # ATR  MA的M0平均
        self.HH.input(kline.high, promotion * arge)  # arge周期的最高
        self.LL.input(kline.low, promotion * arge)  # arge周期的最低
        self.atr = self.Matr.ma  # 波动率
        self.REFHL = [kline.high, kline.low, kline.close, kline.open]
        self.HBS = self.HH.H - N * self.atr
        self.LBS = self.LL.L + N * self.atr
    #//////////////////////////////////////////////////////////////////////////////
class DPO:  #
    '''DPO'''
    def __init__(self, mark=0):
        self.mark = mark
        self.MAN, self.MADPO,self.MADP1,self.DPN,self.DPO=MA(),MA(),MA(),[],0
    def input(self, price, promotion=1, N=12, M0=6, M1=12):
        self.MAN.input(price, N, promotion)
        self.DPN.append(self.MAN.ma)
        self.DPO = (price - self.DPN[-int(promotion * N / 2 + 2)]) if (
                len(self.DPN) >= int(promotion * N / 2 + 2)) else (price - self.DPN[0])
        self.MADPO.input(self.DPO, M0, promotion)
        self.MADP1.input(self.DPO, M1, promotion)
        self.DPN = self.DPN[-promotion * N:]
#//////////////////////////////////////////////////////////////////////////////
class ChiP:
    '''筹码分布'''
    def __init(self):
        self.chips=[0 for x in range(100)]
        self.H,self.L,self.P=0,0,0
    def input(self,kline,Num):
        ###计算筹码边界↓
        if kline.high>self.H:self.H=kline.high
        if kline.low <self.L:self.L=kline.low 
        self.P=(self.H-self.L)/100
        ###计算K线分布粒度↓
        h = int((kline.high-self.L)//self.P)
        l = int((kline.low -self.L)//self.P)
        v = kline.volume*4/((h-l)**2) if h>l else 0
        for x in range(l,h):self.chips[x] += min(h-x,x-l) * v
#//////////////////////////////////////////////////////////////////////////////
def InCrP(NC, RC,pro = 100 ):
    '''涨幅'''
    return pro * ((NC - RC) / RC) if RC != 0 else 0
class NDInCrP:
    '''N日涨跌幅'''
    def __init__(self, mark=0):
        self.mark = mark
        self.InCrPN, self.PrC = [0, ] * 5, [0, ] * 1000

    def input(self, price, arges=[5, 12, 21, 60, 125]):
        self.PrC.append(price)
        self.PrC = self.PrC[-2 * (max(arges)):]
        self.InCrPN = [InCrP(price, self.PrC[-i]) for i in arges]
#//////////////////////////////////////////////////////////////////////////////
class DuaTon:
    '''持续增量'''
    def __init__(self, mark=0):
        self.mark = mark
        self.dtup, self.DTMA, self.dtupN, self.dtups = 0, MA(), [EMA() for i in range(3)],[0,]*3
    def input(self, oi, arges=[5, 12, 21],N=3,promotion=1):
        self.dtup = oi - self.DTMA.ma
        self.DTMA.input(oi,N*promotion)
        for i in range(3): self.dtupN[i].input(self.dtup, arges[i],promotion)
        self.dtups = [self.dtupN[i].ema for i in range(3)]
class KlineCO:
    '''最强实体'''
    def __init__(self, mark=0):
        self.mark = mark
        self.OCS, self.Mk ,self.CO= [0, ] * 200, 0,0
    def input(self, kline, N=200):
        self.CO  =abs(kline.close - kline.open)
        self.OCS.append(self.CO)
        self.OCS = self.OCS[-N:]
        self.Mk  = max(self.OCS)
#//////////////////////////////////////////////////////////////////////////////
class TPFKUD:  #
    '''假突破顶底'''
    def __init__(self, mark=0):
        self.mark = mark
        self.HH, self.LL, self.stats, self.REFstats, self.REFHL = HLV(), HLV(), 0, 0, [1, ] * 4

    def input(self, kline, arge=5):
        self.HH.input(kline.high, arge)
        self.LL.input(kline.low, arge)
        if ((kline.high >= self.HH.H) | (self.REFHL[0] >= self.HH.H)) & (
                kline.close < self.REFHL[2]): self.stats = -2  # 上涨假突破
        if ((kline.low <= self.LL.L) | (self.REFHL[1] <= self.LL.L)) & (
                kline.close > self.REFHL[2]): self.stats = 2  # 下跌假突破
        if (self.REFstats == -2) & (kline.low <= self.REFHL[1]): self.stats = -1  # 上涨假突破
        if (self.REFstats == 2) & (kline.high >= self.REFHL[0]): self.stats = 1  # 下跌假突破
        self.REFHL = [kline.high, kline.low, kline.close, kline.open]
        self.REFstats = self.stats
#//////////////////////////////////////////////////////////////////////////////
class RBREAK:
    '''RBREAK'''
    def __init__(self, kline, mark=0):
        self.mark = mark
        self.UPCond, self.DWCond, self.SixClose, self.DTKs, self.BS, self.REFkline = 0, 0, [1, ] * 7, 0, 0, kline

    def input(self, kline, RHLCO):
        self.DTKs += 1
        self.SixClose[0] = (RHLCO.high + RHLCO.low + RHLCO.close) / 3  # 中线
        self.SixClose[1] = RHLCO.high + 2 * (self.SixClose[0] - RHLCO.low)  # 突破趋势线
        self.SixClose[2] = RHLCO.low - 2 * (RHLCO.high - self.SixClose[0])  # 突破趋势线
        self.SixClose[3] = self.SixClose[0] + (RHLCO.high - RHLCO.low)  # 观察线
        self.SixClose[4] = self.SixClose[0] - (RHLCO.high - RHLCO.low)  # 观察线
        self.SixClose[5] = 2 * self.SixClose[0] - RHLCO.low  # 反转趋势线
        self.SixClose[6] = 2 * self.SixClose[0] - RHLCO.high  # 反转趋势线
        # ======================================================================
        self.UPCond = self.DTKs if self.REFkline.high > self.SixClose[3] else self.UPCond
        self.DWCond = self.DTKs if self.REFkline.low < self.SixClose[4] else self.DWCond
        # ======================================================================
        ###反转多空###
        if (kline.close > self.SixClose[6]) & (self.DWCond > self.UPCond): self.BS = 1
        if (kline.close < self.SixClose[5]) & (self.DWCond < self.UPCond): self.BS = -1
        ###趋势多空###
        if kline.close > self.SixClose[1]: self.BS =  2
        if kline.close < self.SixClose[2]: self.BS = -2
        # ======================================================================
        self.REFkline = copy.deepcopy(kline)
#//////////////////////////////////////////////////////////////////////////////
class TJD:  #
    '''投机度'''
    def __init__(self, mark=0):
        self.mark = mark
        self.MAV, self.MAI, self.Tjd = MA(), MA(), 1

    def input(self, VOL, OI, promotion=1, arge=5):
        self.MAV.input(VOL, arge, promotion)
        self.MAI.input(OI, arge, promotion)
        self.Tjd = self.MAV.ma / self.MAI.ma  if  self.MAI.ma!=0 else 0
        self.tjd = VOL / OI if OI!=0 else 0
#//////////////////////////////////////////////////////////////////////////////
def TwoHL(RHL, listHL, i, NUM=2):
    '''#倒数第NUM个高低'''
    for HL in reversed(listHL):
        if abs(i) > NUM: break
        if (i > 0) & (RHL < HL): RHL, i = HL, (i + 1)  # 取高
        if (i < 0) & (RHL > HL): RHL, i = HL, (i - 1)  # 取低
    return RHL
class COUNTBACKL:  #
    '''顾比倒数线'''
    def __init__(self, mark=0):
        self.mark = mark
        self.Hs, self.Ls, self.BL, self.SL = [], [], 0, 0
    def input(self, kline, M=5, N=2):
        self.Hs.append(kline.high)
        self.Ls.append(kline.low)
        HMAX, LMIN = max(self.Hs[-M:]), min(self.Ls[-M:])
        if kline.high >= HMAX: self.SL = TwoHL(kline.low, self.Ls, -1, NUM=N)  # 创新高，更新空入场价
        if kline.low <= LMIN: self.BL = TwoHL(kline.high, self.Hs, 1, NUM=N)  # 创新低，更新空入场价
#//////////////////////////////////////////////////////////////////////////////

class HOLCPer:
    def __init__(self):
        self.CREFO = 0.0  # 今日开盘价上X周期开盘价比值
        self.CREFC = 0.0  # 今日收盘价上X周期收盘价比值
        self.CREFH = 0.0  # 今日收盘价上X周期最高价比值
        self.CREFL = 0.0  # 今日收盘价上X周期最低价比值

        self.OREFO = 0.0  # 今日开盘价上X周期开盘价比值
        self.OREFC = 0.0  # 今日开盘价上X周期收盘价比值
        self.OREFH = 0.0  # 今日开盘价上X周期最高价比值
        self.OREFL = 0.0  # 今日开盘价上X周期最低价比值

        self.LREFC = 0.0  # 今日最低价上X周期收盘价比值
        self.LREFH = 0.0  # 今日最低价上X周期最高价比值
        self.LREFO = 0.0  # 今日最低价上X周期开盘价比值
        self.LREFL = 0.0  # 今日最低价上X周期最低价比值

        self.HREFL = 0.0  # 今日最高价上X周期最低价比值
        self.HREFO = 0.0  # 今日最高价上X周期开盘价比值
        self.HREFC = 0.0  # 今日最高价上X周期收盘价比值
        self.HREFH = 0.0  # 今日最高价上X周期最高价比值
        self.RefNum = 0  # 上X周期

class KPers:
    def __init__(self, arges):
        self.Num = 0
        self.Arges = arges
        self.UPDW = [0] * len(arges)
        self.HOLCPers = [HOLCPer() for _ in range(len(arges))]
        self.ArgeMAX = max(arges)
        self.Klines = []

    def Input(self,kline  ):
        '''输入K线计算参数属性'''
        ## 复制K线
        self.Klineself.append(copy.deepcopy(kline))  
        if self.Num == 0 :
            self.Klineself.append(copy.deepcopy(kline)) 
        lennum =len(self.Klines)
        ## 遍历参数获取属性
        for i, arge in  self.Arges :
            self.HOLCPers[i].RefNum = arge
            if lennum <= (arge) :arge = lennum - 1
            argeindex =lennum - arge - 1  
            self.HOLCPers[i].CREFO = 100 * ((kline.Close - self.Klines[argeindex].Open) / self.Klines[argeindex].Open)
            self.HOLCPers[i].CREFH = 100 * ((kline.Close - self.Klines[argeindex].High) / self.Klines[argeindex].High)
            self.HOLCPers[i].CREFC = 100 * ((kline.Close - self.Klines[argeindex].Close) / self.Klines[argeindex].Close)
            self.HOLCPers[i].CREFL = 100 * ((kline.Close - self.Klines[argeindex].Low) / self.Klines[argeindex].Low)

            self.HOLCPers[i].HREFL = 100 * ((kline.High - self.Klines[argeindex].Low) / self.Klines[argeindex].Low)
            self.HOLCPers[i].HREFO = 100 * ((kline.High - self.Klines[argeindex].Open) / self.Klines[argeindex].Open)
            self.HOLCPers[i].HREFC = 100 * ((kline.High - self.Klines[argeindex].Close) / self.Klines[argeindex].Close)
            self.HOLCPers[i].HREFH = 100 * ((kline.High - self.Klines[argeindex].High) / self.Klines[argeindex].High)

            self.HOLCPers[i].LREFL = 100 * ((kline.Low - self.Klines[argeindex].Low) / self.Klines[argeindex].Low)
            self.HOLCPers[i].LREFO = 100 * ((kline.Low - self.Klines[argeindex].Open) / self.Klines[argeindex].Open)
            self.HOLCPers[i].LREFC = 100 * ((kline.Low - self.Klines[argeindex].Close) / self.Klines[argeindex].Close)
            self.HOLCPers[i].LREFH = 100 * ((kline.Low - self.Klines[argeindex].High) / self.Klines[argeindex].High)

            self.HOLCPers[i].OREFL = 100 * ((kline.Open - self.Klines[argeindex].Low) / self.Klines[argeindex].Low)
            self.HOLCPers[i].OREFO = 100 * ((kline.Open - self.Klines[argeindex].Open) / self.Klines[argeindex].Open)
            self.HOLCPers[i].OREFC = 100 * ((kline.Open - self.Klines[argeindex].Close) / self.Klines[argeindex].Close)
            self.HOLCPers[i].OREFH = 100 * ((kline.Open - self.Klines[argeindex].High) / self.Klines[argeindex].High)
            if kline.Period == "1440" : self.MarkUPDW(i, argeindex, kline)  
        self.Num+=1
        if lennum > (self.ArgeMAX + 1) :  self.Klines = self.Klines[lennum-self.ArgeMAX:]

    def MarkUPDW(self,i , argeindex , kline ) :
        '''涨跌停标记计算'''
        self.UPDW[i] = 0  
        if argeindex < 1 :  return
        Ecode = kline.Code[7:] 
        Scode = kline.Code[:2] 
        CREFC = 100 * ((self.Klines[argeindex].Close - self.Klines[argeindex-1].Close) / self.Klines[argeindex-1].Close) 
        LREFC = 100 * ((self.Klines[argeindex].Low - self.Klines[argeindex-1].Close) / self.Klines[argeindex-1].Close)    
        HREFC = 100 * ((self.Klines[argeindex].High - self.Klines[argeindex-1].Close) / self.Klines[argeindex-1].Close)   
        self.UPLimit(i, Ecode, Scode, self.Klines[argeindex], HREFC, CREFC) 
        self.DWLimit(i, Ecode, Scode, self.Klines[argeindex], LREFC, CREFC) 
    def UPLimit(self, i , Ecode , Scode , kline , HREFC, CREFC ) :
        '''涨停标记'''
        ZTCDSZSH = (((Ecode == "SZ") and (Scode == "30") and (kline.TradeDate >= "2020-08-24")) or (Ecode == "SH" and Scode == "68"))
        ZTCDBJ   = (Ecode == "BJ")
        ZTZB     = ( not ZTCDBJ) and (not ZTCDSZSH)
        if HREFC >= 9.9 and ZTZB :## //主板10%
            self.UPDW[i] = 2
        if HREFC >= 19.85 and ZTCDSZSH :## //创业板 科创板 20%
            self.UPDW[i] = 2
        if HREFC >= 29.85 and ZTCDBJ :## //北交所 30%
            self.UPDW[i] = 2
        if CREFC >= 9.9 and ZTZB :## //主板10%
            self.UPDW[i] = 1
        if CREFC >= 19.85 and ZTCDSZSH:##//创业板 科创板 20%
            self.UPDW[i] = 1
        if CREFC >= 29.85 and ZTCDBJ :##//北交所 30%
            self.UPDW[i] = 1
        if (self.UPDW[i] == 1) and (kline.Low == kline.High) :##
            self.UPDW[i] = 3 ## 一字板
    def DWLimit(self,  i , Ecode , Scode , kline , LREFC, CREFC ):
        '''跌停标记'''
        DWCDBJ = (Ecode == "BJ")
        DWCDSZSH = (((Ecode == "SZ") and (Scode == "300") and (kline.TradeDate >= "2020-08-24")) or (Ecode == "SH" and Scode == "688"))
        DTZB = (not DWCDBJ )and (not DWCDSZSH)
        if LREFC <= -9.9 and DTZB :## //主板10%
            self.UPDW[i] = -2
        if LREFC <= -19.85 and DWCDSZSH :##//创业板 科创板 20%
            self.UPDW[i] = -2
        if LREFC <= -29.85 and DWCDBJ :## //北交所 30%
            self.UPDW[i] = -2
        if CREFC <= -9.9 and DTZB :## //主板10%
            self.UPDW[i] = -1
        if CREFC <= -19.85 and DWCDSZSH :##//创业板 科创板 20%
            self.UPDW[i] = -1
        if CREFC <= -29.85 and DWCDBJ :##//北交所 30%
            self.UPDW[i] = -1
        if (self.UPDW[i] == -1) and (kline.Low == kline.High):## 
            self.UPDW[i] = -3 ## 一字板
#//////////////////////////////////////////////////////////////////////////////
class Overlap:
    '''K线重叠度'''
    def __init__(self, mark=0):
        self.mark = mark
        self.olp = 0#重叠度
        self.hlp = 0#高低比
    def input(self, NK, RK):
        HH, LL = max(NK.high, RK.high), min(NK.low, RK.low)
        LH, HL = min(NK.high, RK.high), max(NK.low, RK.low)
        MHL = ((NK.high - NK.low) + (RK.high - RK.low))
        self.hlp = abs(LH-HL)/abs(HH-LL) if abs(HH-LL) !=0         else 0
        self.olp = (LH - HL) / (MHL / 2) if (LH > HL) & (MHL != 0) else 0
        
#//////////////////////////////////////////////////////////////////////////////
class HL123:  #
    '''N日高低破'''
    def __init__(self, mark=0):
        self.mark = mark
        self.Hs, self.Ls, self.BL, self.SL, self.B, self.S = [], [], [], [], 0, 0
    def input(self, kline, M=5):
        self.Hs.append(kline.high)
        self.Ls.append(kline.low)
        HMAX, LMIN = max(self.Hs[-M:]), min(self.Ls[-M:])
        if kline.high >= HMAX: self.BL = [kline.high]
        if kline.low <= LMIN: self.SL = [kline.low]
        if kline.high < self.BL[-1]: self.BL.append(kline.high)
        if kline.low > self.SL[-1]: self.SL.append(kline.low)
        self.B = self.BL[-1] if len(self.BL) > 2 else self.SL[-1]
        self.S = self.SL[-1] if len(self.SL) > 2 else self.BL[-1]
#//////////////////////////////////////////////////////////////////////////////
class PiPeLine:
    '''拟合通道'''
    def __init__(self, mark=0):
        self.mark = mark
        self.bmx,self.bmn,self.ks,self.xl,self.YP  =0,0,[],0,MA()
    def input(self,kline,N,promotion):
        N=promotion*N
        self.ks.append(copy.deepcopy(kline))
        self.ks=self.ks[-N:]
        N=len(self.ks)#刷新数量
        self.YP.input(kline.close,N)
        ###计算斜率,通道边界
        xp,yp=(N-1)/2,self.YP.ma#
        self.xl  = sum([self.ks[x].close*x-xp*yp for x in range(N)])/sum([x**2-xp*xp for x in range(N)])
        self.bmx = max([self.ks[x].high-self.xl*x for x in range(N)])
        self.bmn = min([self.ks[x].low -self.xl*x for x in range(N)])
#//////////////////////////////////////////////////////////////////////////////
class DKmark:
    '''攻击波|回头波|涨跌幅'''
    def __init__(self, mark=0):
        self.Drpg, self.Dgjb, self.Dhtb, self.gjb, self.htb = 0, 0, 0, 0, 0
    def input(self, kline, RHLCO, HLCO):
        self.Drpg = 100 * (kline.close - RHLCO.close) / RHLCO.close if RHLCO.close != 0 else 0  # 隔日涨幅
        self.Dgjb = 100 * (kline.close - RHLCO.high) / RHLCO.high if RHLCO.high != 0 else 0  # 隔日攻击波
        self.Dhtb = 100 * (kline.close - RHLCO.low) / RHLCO.low if RHLCO.low != 0 else 0  # 隔日回头波
        self.gjb  = 100 * (kline.close - HLCO.high)/ HLCO.high if HLCO.high != 0 else 0  # 当日攻击波
        self.htb  = 100 * (kline.close - HLCO.low)/ HLCO.low if HLCO.low != 0 else 0  # 当日回头波
#//////////////////////////////////////////////////////////////////////////////
def CutLoss(self,现值,当前回撤,最小回撤=5,回控倍数=2):
    '''回撤控制'''
    if 现值==0: return (最小回撤/100)
    截断亏损=(现值-现值*回控倍数*当前回撤/100)/现值 if (当前回撤>最小回撤) else 1
    return 截断亏损 if (截断亏损>0)&(现值>0) else (最小回撤/100)
#//////////////////////////////////////////////////////////////////////////////
class GTBIAS:
    '''BIAS'''
    def __init__(self, mark=0):
        self.BiaSs=[0,]*3
        self.EMAs = [EMA() for i in range(3)]
    def input(self,high, price,es=[5,12,21],promotion=1):
        for i in range(3):
            self.EMAs[i].input(price, es[i], promotion)
            self.BiaSs[i]=100*(high-self.EMAs[i].ema)/self.EMAs[i].ema  if self.EMAs[i].ema !=0 else 0
class B0SN:  #
    '''交易信号中间过度:-1 0 1 '''
    def __init__(self, mark=0):
        self.mark = mark
        self.B0S = {"REFls": 0, "REsv": 1}
    def input(self, ls):
        if ls != self.B0S["REFls"]:
            self.B0S["REsv"] = 0 if (ls != 0) | (self.B0S["REFls"] != 0) else 1
            self.B0S["REFls"] = ls
#//////////////////////////////////////////////////////////////////////////////
class HLLH:  #
    '''高低突破回档线'''
    def __init__(self, mark=0):
        self.mark = mark
        self.HLLHS={"H":[0,]*1000,"L":[0,]*1000,"HL":[0,]*1000,"LH":[0,]*1000}
        self.HLLHV={"H":0,"L":0,"HL":0,"LH":0,"REFHL":0,"REFLH":0}
        self.arges=list(self.HLLHS.keys())
    def input(self, kline, NDT=21, DNM=1):  #
        self.HLLHS["H"].append(kline.high)    
        self.HLLHS["L"].append(kline.low)    
        self.HLLHS["HL"].append(kline.low)    
        self.HLLHS["LH"].append(kline.high)
        for arge in self.arges:self.HLLHS[arge]=self.HLLHS[arge][-2*NDT:]
        self.HLLHV["H"] = max(self.HLLHS["H"][-NDT:])#NDT的最大值
        self.HLLHV["L"] = min(self.HLLHS["L"][-NDT:])#NDT的最小值
        self.HLLHV["HL"]= max(self.HLLHS["HL"][-NDT:])#NDT的最大的最小值
        self.HLLHV["LH"]= min(self.HLLHS["LH"][-NDT:])#NDT的最小的最大值
        self.HLLHV["REFHL"]= max(self.HLLHS["HL"][-(NDT+DNM):-DNM])#NDT的最大的最小值
        self.HLLHV["REFLH"]= min(self.HLLHS["LH"][-(NDT+DNM):-DNM])#NDT的最小的最大值
    
#//////////////////////////////////////////////////////////////////////////////
class SlopeM:  #
    '''斜率'''
    def __init__(self, mark=0):
        self.mark = mark
        self.xl, self.REMA, self.REMS, self.EMA, self.EMXL = 0, 1, [1,] * 100000, EMA(), EMA()
    def input(self, price, promotion=1,e0=12):
        self.EMA.input(price, e0, promotion)
        XL = 10000 * (self.EMA.ema - self.REMA) / self.REMA  if self.REMA!=0 else 0
        self.EMXL.input(XL, e0, promotion)
        self.REMA = self.REMS[-promotion*e0] if promotion*e0<len(self.REMS)  else self.REMS[0]
        self.REMS.append(self.EMA.ema)
        self.REMS = self.REMS[-promotion*e0*2:]
        self.xl = self.EMXL.ema
#//////////////////////////////////////////////////////////////////////////////
def CROSX(a, b, ra, rb):  #
    '''金叉死叉判断'''
    if (a > b) & (ra <= rb): return 1  # 金叉
    if (a < b) & (ra >= rb): return -1  # 死叉
    if (a > b) & (ra > rb): return 2  #
    if (a < b) & (ra < rb): return -2  #
    else:return 0
#//////////////////////////////////////////////////////////////////////////////
class MDTS:  #
    '''跨月序列'''
    def __init__(self, mark=0):
        self.mark = mark
        self.RDT, self.NDT, self.MDN, self.RMDT = 28, 1, 1, 21
    def input(self, kline, closetime):
        from datetime import datetime
        dt = datetime.fromtimestamp(kline.time)
        self.NDT = int(str(dt)[-11:-9])
        if (kline.time % 86400 == closetime):
            self.MDN += 1  # 当月第几天
            if self.RDT > self.NDT: 
                self.RMDT, self.MDN = self.MDN, 1  # 跨月
                self.RDT = self.NDT
                return True
            else:
                self.RDT = self.NDT
                return False
class WDTS:  #
    '''跨周序列'''
    def __init__(self, mark=0):
        self.mark = mark
        self.RDT, self.NDT, self.WDN, self.RWDT = 0, 0, 0, 0
    def input(self, kline):
        from datetime import datetime
        dt = datetime.fromtimestamp(kline.time)
        self.NDT = dt.weekday()#本周第几天
        if self.RDT > self.NDT: 
            self.RWDT=self.WDN#本年第几周
            self.WDN=dt.isocalendar()[1]
            self.RDT = self.NDT
            return True
        else:return False
#//////////////////////////////////////////////////////////////////////////////
def WaveHL(listS, ToBo=2):  #
    '''波峰波谷 2底部-2顶部'''
    import numpy as np
    try:
        listS = list(np.diff(np.sign(np.diff(listS))))
        TB = listS.index(ToBo) + 1
        return TB
    except:
        return 0
#//////////////////////////////////////////////////////////////////////////////
class BBI:
    def __init__(self, mark=0):
        self.mark = mark
        self.BBI, self.MA03, self.MA06, self.MA12, self.MA24 = 0, MA(), MA(), MA(), MA()
    def input(self, price, N0=3, N1=6, N2=12, N3=24, promotion=1):
        self.MA03.input(price, N0, promotion)
        self.MA06.input(price, N1, promotion)
        self.MA12.input(price, N2, promotion)
        self.MA24.input(price, N3, promotion)
        self.BBI = (self.MA03.ma + self.MA06.ma + self.MA12.ma + self.MA24.ma) / 4
#//////////////////////////////////////////////////////////////////////////////
class MABS:
    def __init__(self, Num=720, mark=0):
        self.mark, self.Num = mark, Num
        self.HREF, self.LREF, self.CREF, self.OREF = 1, 1, 1, 1
        self.Datas, self.BSDK, self.EMABS = [[1, ] * 4], 0, EMA()
    def input(self, kline, e0=12, promotion=1):
        price, self.promotion = kline.close, promotion
        self.EMABS.input(price, e0, self.promotion)
        UDS = 1 if (price >= self.EMABS.ema) else 0
        if (UDS == 0) & (self.LREF > kline.low):
            self.BSDK = -2  # 线下创新低|顺跌
        if (UDS == 1) & (self.HREF < kline.high):
            self.BSDK = 2  # 线上创新高|顺涨
        if (UDS == 1) & (self.LREF > kline.low):
            self.BSDK = 1  # 线上创新低|逆涨
        if (UDS == 0) & (self.HREF < kline.high):
            self.BSDK = -1  # 线下创新高|逆跌
        if (self.LREF > kline.low) & (self.HREF < kline.high):
            self.BSDK = 3  # 即创新高又创新低|发散K
        if (self.LREF <= kline.low) & (self.HREF >= kline.high):
            self.BSDK = -3  # 即不创新高又不创新低|收敛K
        self.HREF, self.LREF, self.CREF, self.OREF = kline.high, kline.low, kline.close, kline.open
        self.Datas.append([kline.high, kline.low, kline.close, kline.open])
        self.Datas = self.Datas[-self.Num:]
#//////////////////////////////////////////////////////////////////////////////
class MACD:
    def __init__(self, mark=0):
        self.mark = mark
        self.RE12,self.RE26=0,0
        self.REFmacd, self.REFdea, self.REFdif=0,0,0
        self.REF2macd, self.REF2dea, self.REF2dif=0,0,0
        self.macd, self.dea, self.dif, self.MA26, self.EMA26, self.EMA12, self.EMA09 = 0, 0, 0, MA(), EMA(), EMA(), EMA()
        self.upnum,self.dwnum,self.stats,self.crux,self.Cline,self.REFST=0,0,0,0,0,0###1:A 2:B 3:C 4:D,Cline临界价
        self.UPMJ,self.DWMJ,self.REFUPMJ,self.REFDWMJ,self.scoreUP,self.scoreDW=0,0,0,0,0,0###前后面积比较
    def input(self, price, promotion=1, e12=12, e26=26, e9=9,sl=False,limit=1):
        '''  
        price价格 promotion扩张倍数 e12=12, e26=26, e9=9,sl慢线使用MA,limit状态切换阈值
        promotion : 1,2,5,10,25,50,125,250
        '''
        self.MA26.input(price, e26, promotion)
        self.EMA26.input(price, e26, promotion)
        self.EMA12.input(price, e12, promotion)
        self.dif  = (self.EMA12.ema - self.MA26.ma) if sl else  (self.EMA12.ema - self.EMA26.ema)###使用MA可以减少毛刺
        self.EMA09.input(self.dif, e9, promotion)
        self.dea  = self.EMA09.ema
        self.macd = (self.dif - self.dea) * 2
        ###////////////////////////////////////////////////////////////////////
        #金叉#死叉
        if (self.macd>=0 and self.REFmacd<0)or (self.macd<=0 and self.REFmacd>0):
            if self.macd>0:#金叉
                self.UPMJ=0
                self.REFDWMJ=self.DWMJ
            if self.macd<0:#死叉
                self.DWMJ=0
                self.REFUPMJ=self.UPMJ
            self.upnum,self.dwnum,self.stats,self.crux,self.REFST=0,0,1,0,self.stats
        if self.macd>0:self.UPMJ+=self.macd#金叉
        if self.macd<0:self.DWMJ+=self.macd#死叉
        ###ABCD////////////////////////////////////////////////////////////////
        UPMACD0=(self.macd>0 and self.macd>self.REFmacd)#零轴上,↑
        UPMACD1=(self.macd>0 and self.macd<self.REFmacd)#零轴上,↓
        DWMACD0=(self.macd<0 and self.macd<self.REFmacd)#零轴下,↓
        DWMACD1=(self.macd<0 and self.macd>self.REFmacd)#零轴下,↑
        if UPMACD0:self.upnum+=1###顺波数量
        if UPMACD1:self.dwnum+=1###逆波数量
        if DWMACD0:self.dwnum+=1###顺波数量
        if DWMACD1:self.upnum+=1###逆波数量
        ###////////////////////////////////////////////////////////////////////
        ###零轴上ABCD
        if UPMACD0 and self.dwnum< limit:self.stats=1#A
        if UPMACD0 and self.dwnum>=limit:self.stats=3#C
        # if UPMACD1 and self.dwnum>=prd and self.stats<=2:self.stats=2#B
        if self.stats<3 and UPMACD1:self.stats=2#B
        if UPMACD1 and self.dwnum> limit and self.stats>=3:self.stats=4#D
        ###////////////////////////////////////////////////////////////////////
        ###零轴下ABCD
        if DWMACD0 and self.upnum< limit:self.stats=1
        if DWMACD0 and self.upnum>=limit:self.stats=3
        # if DWMACD1 and self.dwnum>=prd and self.stats<=2:self.stats=2
        if self.stats<3 and DWMACD1:self.stats=2#B
        if DWMACD1 and self.upnum> limit and self.stats>=3:self.stats=4
        ###////////////////////////////////////////////////////////////////////
        ###关键点序列↓
        if self.crux>0:self.crux+=1#关键点距离计数
        if (UPMACD1 and self.REFmacd>self.REF2macd)or(DWMACD1 and self.REFmacd<self.REF2macd):self.crux=1
        ###临界线
        self.Cline=(((e12*promotion+1)*(e26*promotion+1))*
                    (((e9*promotion+1)*self.REFmacd+2*(e9*promotion-1)*self.REFdea)/(2*(e9*promotion+1)-4))+
                    (e26*promotion-1)*self.RE26*(e12*promotion+1)-(e12*promotion-1)*self.RE12*(e26*promotion+1)
                      )/(2*(e26*promotion-e12*promotion))
        ###////////////////////////////////////////////////////////////////////
        ###多空界
        self.Score()
        ###////////////////////////////////////////////////////////////////////
        ###后置记录
        self.RE12=self.EMA12.ema
        self.RE26=self.MA26.ma if sl else self.EMA26.ema
        self.REF2macd,self.REF2dea,self.REF2dif=self.REFmacd, self.REFdea, self.REFdif
        self.REFmacd, self.REFdea, self.REFdif =self.macd, self.dea, self.dif
        ###////////////////////////////////////////////////////////////////////
    def Score(self):
        ###级别多空评分1-8
        upbase=[0,8,5,6,4,0,7,2,3,1]
        dwbase=[0,1,3,2,7,0,4,6,5,8]
        dact=int(self.macd/abs(self.macd)) if self.macd!=0 else 1
        self.scoreUP=upbase[self.stats*dact]
        self.scoreDW=dwbase[self.stats*dact]
#//////////////////////////////////////////////////////////////////////////////
class NAZF:  #
    '''有效波动'''
    def __init__(self, mark=0):
        self.mark = mark
        self.NaZF, self.Var, self.Border, self.BorderMA20 = 0, 0, 0, 0
        self.NaZFlist, self.VARlist, self.BorderN, self.MAC5, self.MA20 = [], [], [], MA(), MA()
        self.ReNaZF, self.REFH, self.REFL, self.REFC = 1, 1, 1, 1
    def input(self, kline, promotion=1, e0=5, e20=20, N=25):
        self.NaZFlist.append(self.ReNaZF)
        self.NaZFlist = self.NaZFlist[-e0:]
        self.MAC5.input(kline.close, e0, promotion)
        self.NaZF = ((self.REFH / kline.low - 1) + (kline.high / (self.REFL - abs(kline.close - self.REFC)))) / 2\
                     if (self.REFL - abs(kline.close - self.REFC)) else 0
        self.VARlist.append(kline.close - self.MAC5.ma)
        self.VARlist = self.VARlist[-e0:]
        self.Var     = abs(sum(self.VARlist) / len(self.VARlist)) if len(self.VARlist)!=0 else 0
        self.Border  = (max(self.NaZFlist)) * self.Var
        self.BorderN.append(self.Border)
        self.BorderN = self.BorderN[-N:]
        self.MA20.input(self.Border, e20, promotion)
        self.BorderMA20 = self.MA20.ma
        self.ReNaZF, self.REFH, self.REFL, self.REFC = self.NaZF, kline.high, kline.low, kline.close
#//////////////////////////////////////////////////////////////////////////////
def Entropy(ps,lists,base):
    '''熵'''
    from scipy.stats import entropy
    entropy_a=entropy(ps,lists,base)
    return entropy_a
#//////////////////////////////////////////////////////////////////////////////
class Recursion:
    '''K线重采样'''
    def __init__(self, kline):
        self.kid = 0
        self.open = kline.open
        self.time = kline.time
        self.close = kline.close
        self.high = kline.high
        self.low = kline.low
        self.volume = kline.volume
    def Newkline(self, kline):
        self.kid += 1
        self.open = kline.open
        self.time = kline.time
        self.close = kline.close
        self.high = kline.high
        self.low = kline.low
        self.volume = kline.volume
    def Append(self, kline):
        self.time = kline.time
        if self.high < kline.high: self.high = kline.high
        if self.low > kline.low: self.low = kline.low
        self.close = kline.close
        self.volume += kline.volume
#//////////////////////////////////////////////////////////////////////////////
class CLS:
    '''将dict转化成属性'''
    def __init__(self,json):
        try:
            
            if isinstance(json,dict):self.__dict__.update(json)
            else:self.__dict__.update(json.__dict__)
        except Exception as exception:log.Error(str(exception))
def ChildCLS(CLSA,CHILD:dict={}):
    '''为类添加子属性'''
    try    :return CLSA.__class__(CHILD)
    except :return CLSA
        
def DICT(CLSDATA):
    '''将属性输出为dict'''
    try:return CLSDATA.__dict__
    except Exception as exception:log.Error(str(exception))
def ToCLS(jsdata):
    '''深度dict==>>CLS'''
    if  isinstance(jsdata,dict):
        for key in GETKEY(jsdata):
            jsdata[key]=ToCLS(jsdata[key])
        return CLS(jsdata)
    elif  isinstance(jsdata,list):
        return [ToCLS(dats) for dats in jsdata]  
    else:return jsdata
#//////////////////////////////////////////////////////////////////////////////
class Datum:  #
    '''基准曲线'''
    def __init__(self, initprice=1, time=0, Open=0, high=0, low=0, close=0, volume=0, oi=0, code="", factor=1):
        self.time, self.volume, self.oi, self.code = time, volume, oi, code
        self.open = factor * 100 * (Open - initprice) / initprice
        self.close = factor * 100 * (close - initprice) / initprice
        self.high = factor * 100 * (high - initprice) / initprice
        self.low = factor * 100 * (low - initprice) / initprice
    def appendkline(self, kline):  # 
        '''合并k线，首条k线需要把time清零'''
        if self.time == 0:
            self.__dict__.update(kline.__dict__)
        if self.time < kline.time:
            self.time = kline.time
            if self.high < kline.high: self.high = kline.high
            if self.low > kline.low: self.low = kline.low
            self.close = kline.close
            self.volume += kline.volume
    def summarykline(self,kline):
        '''汇总K线'''
        if self.time == 0:
            self.__dict__.update(kline.__dict__)
        else:
            if self.time < kline.time:self.time = kline.time
            self.low     += kline.low
            self.open    += kline.open
            self.high    += kline.high
            self.close   += kline.close
            self.volume  += kline.volume
            self.oi      += kline.oi
#//////////////////////////////////////////////////////////////////////////////
#%% 分钟转日线
class DayBar:
    def __init__(self,cfg={'open': None, 'high': None, 'low': None, 'close': None, 
                            'volume': None,'amount': None, 'oi': None, 'REFoi': None,
                            'trade_date': None, 'trade_time': None, 'code': None, 
                            'time': 0, 'REFclose': None,'OpenPrice': None, 
                            'HighPrice': None,'LowPrice': None,'REFSetPrice': None,
                            'uplimitprice': None, 'dwlimitprice': None}):
        '''
        {'open': None, 'high': None, 'low': None, 'close': None, 
        'volume': None,'amount': None, 'oi': None, 'REFoi': None,
        'trade_date': None, 'trade_time': None, 'code': None, 
        'time': 0, 'REFclose': None,'OpenPrice': None, 
        'HighPrice': None,'LowPrice': None,'REFSetPrice': None,
        'uplimitprice': None, 'dwlimitprice': None}
        '''
        self.NumT ,self.NumK = 0 ,1
        #传入cfg可继续日线合成
        self.__dict__.update(cfg)
    def update(self,jsdt):
        '''传入Tick数据'''
        kline=CLS(jsdt)
        if self.time == 0:self.__dict__.update(jsdt)
        ##################################################################
        self.oi         = kline.oi   #持仓量
        self.time       = kline.time #时间戳
        self.close      = kline.close#收盘价
        self.REFoi      = kline.REFoi#REF持仓量
        self.volume     = kline.volume#成交量
        self.amount     = kline.amount#成交金额
        self.LowPrice   = kline.LowPrice#当日最低价
        self.HighPrice  = kline.HighPrice#当日最高价
        self.OpenPrice  = kline.OpenPrice#当日开仓价
        self.REFSetPrice= kline.REFSetPrice#结算价
        ##################################################################
        self.trade_time   = ts2str(self.time)
        self.trade_date   = kline.trade_date#交易日期
        self.uplimitprice = kline.uplimitprice#涨停价
        self.dwlimitprice = kline.dwlimitprice#跌停价
        ###价格成交量重采样################################################
        if self.high < kline.high: self.high = kline.high#最高价重采样
        if self.low  > kline.low : self.low  = kline.low #最低价重采样
        if kline.volume!=0:self.NumT+=1#tick计数+1 #没有成交的tick不计数
#////////////////////////////////////////////////////////////////////////////// 
#%% Tick转周期                     
class ToBar:
    """
    tick转Bar | Bar转Bar
    Barcls==>>
        {'open': None, 'high': None, 'low': None, 'close': None, 
        'volume': None,'amount': None, 'oi': None, 'REFoi': None,
        'trade_date': None, 'trade_time': None, 'code': None, 
        'time': 0, 'REFclose': None,'OpenPrice': None, 
        'HighPrice': None,'LowPrice': None,'REFSetPrice': None,
        'uplimitprice': None, 'dwlimitprice': None}
        
    """
    def __init__(self,period=60):
        '''period单位为秒'''
        Barcls= {'open': None, 'high': None, 'low': None, 'close': None, 
                 'volume': None,'amount': None, 'oi': None, 'REFoi': None,
                 'trade_date': None, 'trade_time': None, 'code': None, 
                 'time': 0, 'REFclose': None,'OpenPrice': None, 
                 'HighPrice': None,'LowPrice': None,'REFSetPrice': None,
                 'uplimitprice': None, 'dwlimitprice': None}
        self.__dict__.update(Barcls)
        self.NumT,self.NumK,self.REFNumK=0,0,0
        self.REFtime,self.REFvol,self.REFamo,self.period=0,None,None,period
    def update(self,tick:dict):
        '''更新bar'''
        kline=CLS(tick)#dict->class
        self.REFNumK=self.NumK#每根K线独有序列
        ###--------------------------------------------------------------------
        ###周期范围在范围内就持续更新,刷新范围就刷新K线
        startTime=(kline.time//self.period)*self.period#开始时间
        endTime   = startTime+self.period#结束时间
        ###--------------------------------------------------------------------
        if startTime!=self.REFtime:
            self.NumK+=1#标记新的K;
            self.NumT =1#重新计数tick
            self.__dict__.update(kline.__dict__)#属性赋值
            self.time = endTime #时间戳
            self.amount,self.volume=0,0#重置金额及成交量
            self.trade_time = ts2str(self.time)
        else:
            self.oi         = kline.oi   #持仓量
            self.REFoi      = kline.REFoi#REF持仓量
            self.LowPrice   = kline.LowPrice#当日最低价
            self.HighPrice  = kline.HighPrice#当日最高价
            self.OpenPrice  = kline.OpenPrice#当日开仓价
            self.REFSetPrice= kline.REFSetPrice#结算价
            ##################################################################
            self.trade_date   = kline.trade_date#交易日期
            self.uplimitprice = kline.uplimitprice#涨停价
            self.dwlimitprice = kline.dwlimitprice#跌停价
            ###价格成交量重采样################################################
            if self.high < kline.high: self.high = kline.high#最高价重采样
            if self.low  > kline.low : self.low  = kline.low#最低价重采样
            if kline.volume!=0:self.NumT+=1#tick计数+1
            self.close   = kline.close#收盘价重采样
            ##################################################################
        if self.REFamo!=None:self.amount += (kline.amount-self.REFamo)#独立金额 
        if self.REFvol!=None:self.volume += (kline.volume-self.REFvol)#独立成交量
        self.REFtime,self.REFvol,self.REFamo=startTime,kline.volume,kline.amount#用于超时判断REFtime
#//////////////////////////////////////////////////////////////////////////////        
class TODatK:
    '''
    标准K线中使用
    将json格式K线数据转换成类数据
    '''
    def __init__(self,time=0, Open=0, high=0, low=0, close=0, volume=0,oi=0,num=0.0):
        self.time=time
        self.open=Open
        self.high=high
        self.low=low
        self.close=close
        self.volume=volume
        self.oi=oi
        self.num=num#BS数量
    def appendkline(self,kline):  # 合并k线，首条k线需要把time清零
        if self.time == 0:
            self.__dict__.update(kline.__dict__)
        if self.time < kline.time:
            self.time = kline.time
            if self.high < kline.high: self.high = kline.high
            if self.low > kline.low: self.low = kline.low
            self.close = kline.close
            self.volume += kline.volume
#//////////////////////////////////////////////////////////////////////////////
def MaxDowns(array):  
    '''#list最大回撤及起止索引'''
    maxmoney, maxdown = 0.0000001, 0
    starindex, endindex, indexse = 0, 0, [0, 0]
    for index, current in enumerate(array):
        if current > maxmoney:
            maxmoney = current
            starindex = index
        else:
            downnow = 100 * (maxmoney - current) / maxmoney
            if downnow > maxdown:
                maxdown = downnow
                endindex = index
                indexse = [starindex, endindex]
    return round(maxdown,3), indexse#最大回撤#起止索引
#//////////////////////////////////////////////////////////////////////////////
def EvluateDF(df,weight="weight0"):
    '''
    评估策略基本参数
    '''
    df.set_index('trade_date', inplace=True)
    df.sort_index(ascending=True, inplace=True)
    df['trade_time'] = df['trade_time'].astype(str)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    Columns=list(df.columns)
    if weight!="":
        if weight not in Columns: df[weight]=1.0
        df[weight] = df[weight].astype(float)
    df["close"].iloc[0]=1
    for i in range(1,len(df)):
        if weight!="":
            df["close"].iloc[i]=df["close"].iloc[i]*df[weight].iloc[i]
        df["close"].iloc[i]=df["close"].iloc[i-1]*(1+((df["close"].iloc[i]/100)-1/10000))
    maxDW,maxDWIndex=MaxDowns(df["close"].to_list())#最大回撤和起止点
    days=StrTimeSpan(df["trade_time"].iloc[0],df["trade_time"].iloc[-1])#自然天数
    maxDWstime=df["trade_time"].iloc[maxDWIndex[0]]
    maxDWetime=df["trade_time"].iloc[maxDWIndex[1]]
    maxDWSpan=StrTimeSpan(maxDWstime,maxDWetime)
    rst={
        "自然日(天)":days,
        "最大回撤":round(maxDW,3), 
        "最大回撤stime":maxDWstime,
        "最大回撤etime":maxDWetime,
        "回撤时长(天)":maxDWSpan,
        "总收益率(%)":round(100*(df['close'].iloc[-1]-1),3),
        "每日收益率(%)":round(100*(df['close'].iloc[-1]-1)/days,3),
        "年化收益率(%)":round(100*365*(df['close'].iloc[-1]-1)/days,3),
        "收益回撤比":round((100*365*(df['close'].iloc[-1]-1)/days)/maxDW,3)
        }
    return rst
 
#//////////////////////////////////////////////////////////////////////////////
class MaxLoss:
    '''最大回撤'''
    def __init__(self):
        #当前净值,回撤时长,最大回撤时长,最大净值,当前回撤,最大回撤
        self.NowC,self.Num,self.MaxNum,self.MaxH,self.loss,self.Maxloss=None,0,0,0,0,0
    def input(self,kline):
        self.Num += 1#回撤周期时长
        if self.MaxNum<self.Num:self.MaxNum=self.Num#最大回撤时长
        if self.MaxH<kline.high:self.Num,self.MaxH=0,kline.high#最高净值
        if not self.NowC:self.NowC,self.MaxH=kline.close,kline.close#设置初始净值
        else:self.NowC=kline.low#最低净值
        self.loss = self.MaxH - self.NowC#净值差即回撤
        if self.Maxloss<self.loss:self.Maxloss=self.loss#更新最大回撤
###############################################################################
class RecordBS:
    '''记录交易次数,胜率,盈亏比'''
    def __init__(self):
        #REF交易信号,总交易次数,盈利次数,亏损次数,胜率,策略盈亏比
        self.REFBS,self.TDNum,self.PNum,self.LNum,self.WinPer,self.PLR=0,0,0,0,0,0
        #当前笔初始净值,总盈利,总亏损,平均盈利,平均亏损,当前笔盈亏
        self.InitC,self.PSumM,self.LSumM,self.PMean,self.LMean,self.PLNow=None,0,0,0,0,0.0
        #开始时间,结束时间,自然日时长,净盈亏,盈亏胜率,每日平均,策略年化
        self.Stime,self.Etime,self.Days,self.PLSumM,self.WinPerPLR,self.DayMean,self.YearPL=None,None,0,0,0,0,0.0
    def input(self,BS,kline):
        #######################################################################
        ###跨越多少个自然日
        if not self.Stime:self.Stime=kline.time#开始时间
        self.Etime=kline.time#结束时间
        self.Days=(self.Etime-self.Stime)/86400#天数
        #######################################################################
        ###记录盈亏次数金额,判断上笔盈利否,计算平均盈利亏损
        if self.InitC:#如果持有仓位
            self.PLNow=(kline.close-self.InitC)#盈利数值 
            if   (self.PLNow> 0) and (BS!=self.REFBS):
                self.PNum +=1#盈利次数
                self.PSumM+=self.PLNow#亏损次数
                self.PMean =(self.PSumM/self.PNum)#平均盈利
            elif (self.PLNow<=0) and (BS!=self.REFBS):
                self.LNum +=1#亏损次数
                self.LSumM+=abs(self.PLNow)#亏损金额
                self.LMean =(self.LSumM/self.LNum)#平均亏损
        ###初始化下笔初始值#################################################
        if   (abs(BS)>0) and (BS!=self.REFBS):self.InitC = kline.close
        elif (abs(BS)==0):self.InitC ,self.PLNow = None,0.0
        #######################################################################
        ###基本回测参数计算
        self.TDNum =self.PNum+self.LNum#总交易次数
        self.WinPer=round(100*(self.PNum/self.TDNum),3) if self.TDNum!=0 else 0#胜率
        self.PLR   =self.PMean / self.LMean  if self.LMean !=0  else 0 #盈亏比
        self.PLSumM=self.PSumM-self.LSumM#净盈亏
        self.WinPerPLR= 100/(1+self.PLR)#盈亏胜率
        self.DayMean  = self.PLSumM/self.Days if self.Days!=0 else 0#每日平均收益
        self.YearPL   = self.DayMean*365#策略年化收益
        ###后置记录#############################################################
        self.REFBS=BS
###############################################################################
#%% 标准K线
class StdHOCL:
    '''标准K线'''
    def __init__(self,summary=False):
        '''默认不开启回测统计'''
        self.summary = summary
        self.MaxLoss = MaxLoss()
        self.RecordBS= RecordBS()
        self.kline,self.RKline,self.CZ,self.BS,self.FP,self.LP,self.KLINEs=TODatK(),TODatK(close=0),1.0,1.0,0.0,1.0,[]
    def input(self,kline,BS=1.0,CDT=120,LP=1.0,FP=0.0):
        '''BS买卖信号方向 CDT保留K线数量 LP仓位比  FP手续费比'''
        if kline.close==0:return 
        self.KLINEs.append(copy.deepcopy(kline))
        self.KLINEs=self.KLINEs[-CDT:]#保留记录输入Kline数量
        ########################################################################
        BSKLINE=min(self.RKline.close,kline.close) if BS<0 else self.RKline.close#
        self.FP=FP  if self.BS*self.LP!=BS*LP  else 0.0#如果仓位发生变动则赋值手续费否则是0
        self.BS=self.BS*self.LP#上一次的BS方向和LP仓位比,用于计算新的K线。
        ##标准化HOLC############################################################
        CD=self.BS*(kline.close-self.RKline.close)/BSKLINE  if BSKLINE !=0 else 0
        HD=self.BS*(kline.high -self.RKline.close)/BSKLINE  if BSKLINE !=0 else (kline.high -kline.close)/kline.close
        LD=self.BS*(kline.low  -self.RKline.close)/BSKLINE  if BSKLINE !=0 else (kline.low  -kline.close)/kline.close
        OD=self.BS*(kline.open -self.RKline.close)/BSKLINE  if BSKLINE !=0 else (kline.open -kline.close)/kline.close
        ########################################################################
        self.CZ+=CD#累计赋值
        HZ=max((HD-CD),(OD-CD),(LD-CD),0)+self.CZ#等比平移
        LZ=min((HD-CD),(OD-CD),(LD-CD),0)+self.CZ#等比平移
        OZ=(OD-CD)+self.CZ#等比平移
        ###减手续费率############################################################
        OZ-=self.FP
        HZ-=self.FP
        LZ-=self.FP
        self.CZ-=self.FP
        ###合成K线###############################################################
        self.kline=TODatK(kline.time,OZ,HZ,LZ,self.CZ,kline.volume,kline.oi,self.BS)
        ###汇总交易结果##########################################################
        if self.summary :
            self.MaxLoss.input(self.kline)##计算最大回撤
            self.RecordBS.input(BS*LP,self.kline)##计算胜率,盈亏比等【注传入及时BS参数而不是self.BS】
        ###后置记录##############################################################
        self.RKline,self.BS,self.LP=copy.deepcopy(kline),BS,LP#后置记录
#//////////////////////////////////////////////////////////////////////////////
def FQOHLC(jsdt,fq="qfq",mark=False,OHLC =["high","open","close","low"]):
    '''K线价格复权计算'''
    for key  in  OHLC:
        keyName=f"{fq}{key}" if mark else key
        jsdt[keyName]=jsdt[fq]*jsdt[key]
    return jsdt 
#%% 时间转换
def Sleep(second):
    for x in range(int(second), -1, -1):
        print("\r",f"||休眠倒计时:{x} 秒||",end="", flush=True)
        time.sleep(1)
def ToDaytime():
    '''返回今日零点时间戳'''
    from datetime import date
    return int(time.mktime(date.today().timetuple()))
def ToDaydate(Format='%Y-%m-%d'):
    '''返回今日日期'''
    from datetime import date
    return (date.today()).strftime(Format)
def strTodate(strtime,Format='%Y-%m-%d %H:%M:%S'):
    '''字符串转日期'''
    if isinstance(strtime,str):
        return datetime.strptime(strtime,Format)
    else:return strtime
def NowDatetime(num=19):
    '''返回当前时间'''
    return str(datetime.now())[:num] if isinstance(num, int)  else datetime.now()
def strTotime(strtime,Format='%Y-%m-%d %H:%M:%S'):
    '''
    时间转换:
    日期转时间戳  
    '''
    
    if isinstance(strtime, str) : strtime=time.mktime( time.strptime(strtime,Format))
    else:strtime=time.mktime(strtime.timetuple())
    return strtime
def NowHTime():
    '''当前时刻对应08:30:00的时间戳'''
    return time.time()-ToDaytime()
def HourTime(hourtime:str="08:30:00"):
    '''将日期时间08:30:00转时间戳'''
    return strTotime(f"{ToDaydate()} {hourtime}")-ToDaytime()
def TimeHour(TimeHour:int=28800):
    '''将去日期时间戳转时间08:00:00'''
    return ts2str(ToDaytime()+TimeHour)[-8:]
def ts2str(ts=0,Format='%Y-%m-%d %H:%M:%S'): 
    '''
    ts 时间戳 转时间字符串
    默认0 返回当前时间 字符串
    '''
    if ts == 0:
        return datetime.now().strftime(Format)
    return datetime.fromtimestamp(ts).strftime(Format)
###############################################################################
def CompareTime(TimeA,TimeB,act=max,FormatA='%Y-%m-%d %H:%M:%S',FormatB='%Y-%m-%d %H:%M:%S'):
    '''
    格式可不一样的时间比较大小    
    '''
    return ts2str(act(strTotime(TimeA,FormatA),strTotime(TimeB,FormatB)))
###############################################################################
def StrTimeSpan(strstime, stretime,format='%Y-%m-%d %H:%M:%S'):
    '''
    获取字符串日期之间的时间间隔（以天为单位）
    '''
    start_date = datetime.strptime(strstime,format) # 将日期字符串转换为日期对象
    end_date = datetime.strptime(stretime, format) # 将日期字符串转换为日期对象
    time_delta = end_date - start_date# 计算时间差
    time_interval = time_delta.days# 提取出时间间隔（以天为单位）
    return time_interval
###############################################################################
def subTimeN(s_time="",e_time="",days=0,daye=0):
    '''
    时间边界
    回测确定时间起止边界
    '''
    NowdateN=str(datetime.now().date())#当前时间日期
    if s_time == '':    # 开始时间为空，由结束时间倒推开始时间
        if e_time == '': e_time = str(datetime.strptime(NowdateN, '%Y-%m-%d') - timedelta(days=daye))
        s_time = str(datetime.strptime(str(e_time), '%Y-%m-%d %H:%M:%S') - timedelta(days=days))
    else:
        if e_time == '': # 开始时间不为空，由开始时间倒推结束时间
            e_time = (datetime.strptime(str(s_time), '%Y-%m-%d %H:%M:%S') + timedelta(days=days))
            if e_time > datetime.strptime(NowdateN, '%Y-%m-%d'): 
                e_time = str(datetime.strptime(NowdateN, '%Y-%m-%d'))
    return s_time,e_time    
#%% 合成多周期K线    
class KLine():
    def __init__(self, time=0, Open=0, high=0, low=0, close=0, volume=0, oi=0, code=""):
        self.volume, self.oi, self.code = volume, oi, code  
        self.time, self.open, self.close, self.high, self.low=time, Open, close, high, low
    def update(self, kline):
        '''合并k线,首条k线需要把time清零'''
        if self.time == 0:
            self.__dict__.update(kline.__dict__)
        if  self.time    < kline.time:
            self.time    = kline.time
            if self.high < kline.high: self.high = kline.high
            if self.low  > kline.low : self.low  = kline.low
            self.close   = kline.close
            self.volume += kline.volume
            
class SpliceK:
    '''由一分钟合成不超过日线级别的周期K线'''
    def __init__(self,period:list=[5,30,60,120,"D"]):
        self.startID = 0#日内计数
        self.period  = period#周期列表
        self.periodNW= {f"New_{x}":True for x in self.period }#结点标志
        self.periodID= {f"start_{x}":0  for x in self.period }#周期计数
        self.KLINES  = {f"Kline_{x}":KLine() for x in self.period }#K线合成
        self.REFKLS  = {f"REFKL_{x}":None    for x in self.period }#上一K线
    def input(self,kline):
        '''更新K线'''
        self.startID+= 1
        for key in GETKEY(self.periodNW):self.periodNW[key]=False#非结束结点
        for key in GETKEY(self.KLINES):self.KLINES[key].update(kline)
    def PeriodX(self,kline):
        '''
        周期结点更新
        放在更新K线命令后，条件命令前
        '''
        DayX=(kline.time%86400==kline.closetimes[3])
        for x in self.period :
            if isinstance(x, str) :#日线级别↓
                if DayX:#日线结束↓
                    self.startID  = 0#交易日结束计数器清0
                    self.periodNW[f"New_{x}"]    = True#结束结点
                    self.periodID[f"start_{x}"] += 1 #周期K计数加1
                    self.REFKLS[f"REFKL_{x}"]=copy.deepcopy(self.KLINES[f"Kline_{x}"])#深度拷贝
            else:#日内级别↓
                if ((self.startID%x==0)|DayX):
                    self.periodNW[f"New_{x}"]    = True#结束结点
                    self.periodID[f"start_{x}"] += 1#周期K计数加1
                    self.REFKLS[f"REFKL_{x}"]=copy.deepcopy(self.KLINES[f"Kline_{x}"])#深度拷贝
    def InitTime(self):
        '''
        初始化结点==>>时间更新==>>新的K线
        放在条件命令之后
        '''
        for x in self.period :
            if self.periodNW[f"New_{x}"]:self.KLINES[f"Kline_{x}"].time = 0#初始化结点
# %% 功能函数
#//////////////////////////////////////////////////////////////////////////////
def DfToType(df,keys:list,types=str):
    '''修改df 的列的数据格式'''
    try:
        for key in keys:
            try:df[key]=df[key].astype(types)
            except:continue
    except Exception as exception:
        log.Error(str(exception))
def SetList(List,Reversed=False,Auto=True):
    """
    一个函数，接受一个列表，可选地对其进行排序和去重。
    
    参数:
    - List: 要操作的元素列表。
    - Reversed: 一个布尔值，指示在处理之前是否要反转列表。
    - Auto: 一个布尔值，指示是否自动对最终列表进行排序而不考虑原来的顺序。
    返回:
    一个去重后的新列表，根据参数可能进行排序。
    """
    if Auto:return sorted(list(set(List)))#简易去重升序且不考虑顺序
    ###去重且考虑原来的排序
    SetLS=[]
    if Reversed:List=list(reversed(List))
    for x in List:
        if x in SetLS:continue
        SetLS.append(x)
    if Reversed:SetLS=list(reversed(SetLS))
    return SetLS
#//////////////////////////////////////////////////////////////////////////////
def UniqueList(List):
    '''返回list中独一无二的元素列表'''
    d = {}
    for elem in List:
        if elem in d:
            d[elem] += 1
        else:
            d[elem] = 1
    return [k for k,v in d.items() if v == 1]   
#//////////////////////////////////////////////////////////////////////////////
def MatchCode(sublist,baselist):
    '''
    品种代码匹配
    '''
    sublist = list(set([x.upper() for x in sublist]+sublist + [x.lower() for x in sublist]))
    sublist = [baselist[i] for i in range(len(baselist)) if (baselist[i] in sublist )]
    return sublist
#//////////////////////////////////////////////////////////////////////////////
def SplitList(data,length=8000,splitnum=2000):
    """
    将列表分割
    """
    Num = len(data)
    if Num>length:
        indexall  =  Num//splitnum
        return [data[i:i+int(Num//indexall)] for i in range(0,Num,int(Num//indexall))]
    else:return [data]
    
def SplitDF(data,length=8000,splitnum=2000):
    '''dataframe 分批次拆解'''
    Num,rst=len(data),[]
    if Num>length:
        cutlists=[i for i in range(0,Num,Num//(Num//splitnum))]
        for i in range(len(cutlists)): 
            if i >=(len(cutlists)-1):df=data[cutlists[i]:]
            else:df=data[cutlists[i]:cutlists[i+1]]
            rst.append(df)
        return rst
    else:return [data]
#////////////////////////////////////////////////////////////////////////////// 
def DF_to_Json(df,orient="records",force_ascii=False):
    '''
    注意:如果有None将会报错
    orient:=>> records 返回的是列表集合||  index返回的是索引字典集合
    force_ascii强制ASCII格式
    '''
    return EVALI(df.to_json(orient=orient,force_ascii=force_ascii))
def Df_to_Html(df, filename='filename', filepath='../Stock_Data/Rob_Money/', encoding='gb18030'):
    '''Df_to_Html'''
    Mkdir(filepath)
    return df.to_html('%s%s.html' % (filepath, filename), encoding=encoding)
#//////////////////////////////////////////////////////////////////////////////
def DifEntSet(listA, listB):  
    '''取在A中不在B的list'''
    return list(set(listA).difference(set(listB)))
def InterSet(listA, listB):
    '''取两个列表的交集'''
    return list(set(listA).intersection(set(listB)))
#//////////////////////////////////////////////////////////////////////////////
def ListItemNum(List:list =[]):
    counts = {}
    for item in List:
        if item in counts:
            counts[item] += 1
        else:
            counts[item] = 1
    return counts
#//////////////////////////////////////////////////////////////////////////////
def RColor(Num=1):
    '''随机颜色'''
    ColorS, colorArr = [], ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    for i in range(Num):
        color = ""
        for i in range(6): color += colorArr[random.randint(0, 14)]
        ColorS.append("#" + color)
    return ColorS
#//////////////////////////////////////////////////////////////////////////////
def UniQLs(List, d={}):
    '''List中独一无二的值,保留其顺序'''
    for elem in List:
        d[elem] = (d[elem] + 1) if elem in d else 1
    return [k for k, v in d.items() if v == 1]
#//////////////////////////////////////////////////////////////////////////////
def RoundUp(number, digit=1):  # 四舍五入digit精度
    '''向上取舍'''
    import math
    return math.ceil(number * (10 ** digit)) / (10 ** digit)
#//////////////////////////////////////////////////////////////////////////////
def RoundDw(number, digit=1):  # 向下取整digit精度
    '''向下取舍'''
    import math
    return math.floor(number * (10 ** digit)) / (10 ** digit)
#%% 多线程多进程
def ThreadPools(max_workers, Fun, arges):
    '''线程池带参数'''
    with ThreadPoolExecutor(max_workers) as executor: executor.map(Fun, arges)
#//////////////////////////////////////////////////////////////////////////////
def ThreadRunA(Funs):
    '''多线程'''
    from threading import Thread
    THDS=[Thread(target=fun) for fun in Funs]
    for thd in THDS:thd.start()
    for thd in THDS:thd.join()
#//////////////////////////////////////////////////////////////////////////////
class TqdmN:  #
    '''进度条'''
    def __init__(self, arges):
        self.pbar  = tqdm(total=arges)  if isinstance(arges, int) else tqdm(total=len(arges)) 
        self.btime = time.strftime("%Y-%m-%d %H:%M:%S")
        self.stime = datetime.now()
        self.etime = time.strftime("%Y-%m-%d %H:%M:%S")
    def update(self,string=None):
        if not string:string="进度"
        ftime = datetime.now()
        rtime = (ftime - self.stime).seconds
        try:
            self.pbar.set_description('\n||■|%s|■||Time Span:%.1f s|■=>>'%(string,rtime))
            self.pbar.update()
        except KeyboardInterrupt:self.pbar.close()
#//////////////////////////////////////////////////////////////////////////////
def ProSl(Fun, arges, maxpool=multiprocessing.cpu_count()):
    '''多进程'''
    # ==========================================================================
    ps = Pool(maxpool)
    TqdmNX=TqdmN(arges)
    for arge in arges:
        ps.apply_async(Fun, args=[arge,], callback=TqdmNX.update)
    ps.close()
    ps.join()
#//////////////////////////////////////////////////////////////////////////////
# import multiprocessing
# def FuncRun(dictdata,mark,markdata):
#     dictdata[mark] = {"mark":markdata}
# def ProcessM():
#   '''多进程'''
#     Manager = multiprocessing.Manager()
#     dictdata= Manager.dict()
#     works=[multiprocessing.Process(target=FuncRun,name=str(i),args=(dictdata, i, i+100)) for i in range(10)]
#     for work in works:work.start()
#     for work in works:work.join()
#//////////////////////////////////////////////////////////////////////////////
#%% 订阅K线
def subKline(code,period="1m",limit=1000,  s_time="",e_time="",suffix= "L9",startk=10000):
    '''
    向服务器请求数据
    最少取3天数据，才能保证下列数据计算完成
    'ks1day'：一天有多少根K线,
    'opentimes'：开盘结点,
    'closetimes'：收盘节点，
    '''
    try:
        ###订阅参数
        if startk==None:startk=10000
        code = f"{code}{suffix}"
        if e_time == "": e_time = ts2str(0)
        if s_time != "" and s_time > e_time: return  pd.DataFrame()
        e_time = ts2str(datetime.strptime(e_time, '%Y-%m-%d %H:%M:%S').timestamp() + 30)
        param = {
                "user": "100000",
                "token": "luhouxiang",
                "code": code,
                "period": period,
                "s_time": s_time,  # 开始时间可以不给出,返回数据全包含起止时间
                "e_time": e_time,  # 结束时间缺省是当前时间
                "count": limit     # 数量在只有结束时间的时候有效，建议不为0
                }
        headers = {'Content-Type': 'application/json;charset=UTF-8', 'Connection': 'keep-alive'}
        requests.DEFAULT_RETRIES = 10 
        s = requests.session() 
        s.keep_alive = False
        try:
            url = 'http://192.168.1.100:8086/api/hqqh/kline'
            r = requests.request('POST', url, json=param, headers=headers,timeout=10)
        except Exception as exception:
            log.Error(str(exception))
            try:
                url = 'http://192.168.1.101:8086/api/hqqh/kline'
                r = requests.request('POST', url, json=param, headers=headers,timeout=10)
            except Exception as exception:
                log.Error(str(exception))
        ###订阅结果
        j = r.json()
        lists = j["result"]['lists'] if j.get('err_code', -1) == 0 else []
        names = j["result"]['names'] if j.get('err_code', -1) == 0 else []
        names=[i.lower()  for i in names ]#全部小写
        ###df数据格式化
        df = pd.DataFrame(lists, columns=names) 
        if df.empty == False:
            df['kid'] = [startk+i for i in range(len(df))]#自定义序列
            df['trade_time'] = pd.to_datetime(df.time, unit='s', origin='1970-01-01 08:00:00')
            df['trade_date'] = (df['trade_time'].apply(lambda x:x.date())).astype('str')
            df['trade_time'] = (df['trade_time']).astype('str')
            df.rename(columns={'openinterest': 'oi'}, inplace=True)
            BaseT=KLitem().init_s(df)
            for item in ['ks1day','opentimes','closetimes']:df[item]=[BaseT[item] for i in range(len(df))]
        if len(lists) == 0: return  pd.DataFrame()
        return df[1:]
    except Exception as exception:log.Error(str(exception))
#//////////////////////////////////////////////////////////////////////////////
class KLitem:
    def __init__(self):
        self.ti = 0
        self.ls = 0
        self.gap = 0
        self.ks1day = 1
        self.lastktime = 0
        self.lastprice = 0
        self.initprice = 1
        self.opentimes = [0, 0, 0, 0]
        self.closetimes = [0, 0, 0, 0]
    def init_s(self, df):
        days = []
        for i in range(len(df)):
            if (2 * 3600 + 15 * 60) < df["time"].iloc[i] % (86400) < (2 * 3600 + 30 * 60):
                self.gap = 1  # 上午没有休盘
                self.closetimes[2] = 0  # 上午只有1段, 1 1 3 0
                self.opentimes[2] = 0  # 上午只有1段, 1 1 3 0
            if i == 0:
                pass
            else:
                t0 = self.Segs(df["time"].iloc[i-1])
                t1 = self.Segs(df["time"].iloc[i]) if i + 1 < len(df) else 0
                if t0 != t1:
                    self.closetimes[t0] = df["time"].iloc[i-1]% (86400)
                    self.opentimes[t1] = df["time"].iloc[i]% (86400)
                    if t0 == 3:
                        days.append(i - self.ti)  # 上一个k先在结算前, 下一k先在结算后
                        self.ks1day = max(days)
                        self.ti = i
            if len(days) > 3: break
        return self.__dict__
    def Segs(self, t):  # 0:夜盘 1:上午盘1 2:上午盘2 3:下午盘
        sec = t % 86400
        if sec < 8400:
            return 1  # 上午10:20 (10-8)*3600+20*60=8400
        elif sec < 18000:
            return int(2 - self.gap)  # 中午 13:00 (13-8)*3600=18000
        elif sec < 36000:
            return 3  # 下午 18:00 (18-8)*3600=36000
        else:
            return 0  # 夜盘
#//////////////////////////////////////////////////////////////////////////////
#%% 数据重采样
def Resample(df,period:str="30min",method="resample",num=2):
    '''行情数据周期重采样'''
    try:
        if len(df)<1:return pd.DataFrame()
        if method=="resample":
            df.index =pd.to_datetime(df["trade_time"])
            aggs = {"trade_date":"last","trade_time":"first","code":"last",
                    "open":"first","high":"max","close":"last","low":"min","volume":"sum"}
            data = df.resample(period, axis=0,closed="right",label="right").agg(aggs).dropna()
            data["period"] = period.replace(delint(period),"")
            data["trade_time"]=data.index#"trade_time":"first"与这里呼应实现实时跨时间更新
        elif method=="groupby":
            df.index =pd.to_datetime(df["trade_time"])
            period = period.replace(delint(period),"")
            idx = list(range(0,len(df)//num))*2
            idx.sort()
            df["idx"] = idx
            aggs = {"trade_date":"last","trade_time":"last","code":"last",
                    "open":"first","high":"max","close":"last","low":"min","volume":"sum"}
            data = df.groupby(by="idx").agg(aggs).dropna()
            data["period"] = period
            del df["idx"]
        return data 
    except:return pd.DataFrame()
def PeriodGP(df,limit=None,minperiod=True):
    '''一次性将1分钟数据合成多周期数据'''
    if len(df)<1:return {key:pd.DataFrame() for key in ["1min","5min","15min","30min","60min","120min"]} 
    if not limit:limit=len(df)
    df05  =Resample(df,"5min")
    df15  =Resample(df,"15min")
    df30  =Resample(df,"30min")
    df60  =Resample(df30,"60min","groupby",2)
    df120 =Resample(df60,"120min","groupby",2)
    if minperiod: return {"1min":df.iloc[-limit:],"5min":df05.iloc[-limit:], "15min":df15.iloc[-limit:],"30min":df30, "60min":df60,"120min":df120}
    else :return {"5min":df05.iloc[-limit:], "15min":df15.iloc[-limit:],"30min":df30, "60min":df60,"120min":df120}


#%% 基础函数
def LoadJS(strjs):
    '''json格式化'''
    import json
    try:return json.loads(strjs)
    except:return strjs
    
def StrSimilar(s1, s2):
    '''文本相似度'''
    import difflib
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()
def GETKEY(JSData):
    '''
    获取Json的KEY
    注意:不要给返回列表排序,否则可能导致严重后果
    '''
    try:return list(JSData.keys())
    except:return []
def RenameDict(jsdt,REFname,NEWname):
    '''dict键值重命名'''
    try:jsdt[NEWname] = jsdt.pop(REFname)
    except:pass
def Float(strs,err=''):
    '''转换成浮点数'''
    try:return float(strs)
    except:return err  if isinstance(err,float) else strs
def Int(strs,err=''):
    '''转换成整数'''
    try:return int(strs)
    except:return err  if isinstance(err,int) else strs
def JsonSTF(JSData):
    '''批量json内容转float'''
    for key in GETKEY(JSData):JSData[key]=Float(JSData[key])
    return JSData
def EVALI(STData):
    '''格式化json list'''
    for i in ["[" , "]" , "{" , "}" ]:
        try:
            if i in STData:
                try:STData=eval(STData)
                except:pass
        except Exception as err: 
            log.Warn(err)
            pass       
    return STData
def delint(strold):  #
    '''字符串去数字'''
    import re
    return re.sub(r'[0-9]+', '', strold)
def delAbc(strold):  #
    '''字符串去字母'''
    import re
    return re.sub(r"[A-Za-z]","",strold) 
def OnlyCHN(txt):
    '''只保留汉字'''
    return re.sub('[^\u4e00-\u9fa5]+','',txt)
def delpunc(string,punc = '~`!#$%^&*()_+-=|\';":/.,?><~·！@#￥%……&（*）\[\]——+-=“：’；、。，？》《{}³²°  '):
    '''删除特殊、标点符号'''
    import re
    return re.sub(r"[%s]+" %punc, "",string)
def get_strtime(text):
    '''从文本中获取年月日日期'''
    text = text.replace("年", "-").replace("月", "-").replace("日", " ").replace("/", "-").strip()
    text = re.sub("\s+", " ", text)
    txt  = ""
    regex_list = [
        "(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2})",# 2013年8月15日 22:46:21
       "(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2})",# "2013年8月15日 22:46"
       "(\d{4}-\d{1,2}-\d{1,2})",# "2014年5月11日"
       "(\d{4}-\d{1,2})"]# "2014年5月"
    for regex in regex_list:
        txt = re.search(regex, text)
        if txt:return txt.group(1)
    log.Info("没有获取到有效日期")
#//////////////////////////////////////////////////////////////////////////////
def BkGdSRun(fun,args):
    '''后台运行函数'''
    from apscheduler.schedulers.background  import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(fun,args=args)
    scheduler.start()

def TryErrMsg(func):
    """
    这是一个装饰器函数，将输入函数封装在 try-catch 块中。
    它接受一个函数对象 'func'，并返回一个新的函数对象 'wrapper'。
    'wrapper' 函数接受任意参数和关键字参数，使用它们调用输入函数 'func'，
    如果调用成功，则返回调用的结果。
    如果调用 'func' 引发异常，则使用 log.Error() 函数记录错误消息，并且不返回任何内容。
    """
    def wrapper(*args, **kwargs):
        try: return func(*args, **kwargs)
        except Exception as err: log.Error(f"||错误|{err}")
    return wrapper

# %% 文本表格化
def Textinfo(title,header=False):
    '''
    本格式化表格
    table.field_names = ['name','age','sex']
    
    table = Textinfo("标题")
    table.add_row([a,b,c,d])
    '''
    table = PrettyTable()
    table.hrules = prettytable.ALL
    table.title = "<<<==%s==>>>" % title
    table.header = header 
    table.junction_char = ' '
    table.align = "c"#"l"
    table.valign = "t"
    return table
# %% 交易撮合
def TrigBS(kline, limitPrice, BSact=0):
    '''交易撮合方式'''
    ###限价买#
    if   BSact > 0:
        if kline.low > limitPrice:return kline.close
        else:return limitPrice if kline.high > limitPrice else kline.high
    ###限价卖#
    elif BSact < 0:
        if kline.high < limitPrice:return kline.close
        else:return limitPrice if kline.low < limitPrice else kline.low 
    else:return kline.close
def LinkSelect(CDs:list=[],CD:str="",link:str="or",bracket=True):
    '''
    将多个条件用or  and 连接 返回字符串 ;bracket:是否用括号约束
    ["code='SA305'", " or code='MA305'", " or code='rb2305'"] ==>> "code='SA305' or code='MA305' or code='rb2305'"
    '''
    if len(CDs)<1:return CD
    for x in range(1,len(CDs)):CDs[x]=f" {link} {CDs[x]} "
    for x in CDs:CD +=x
    if bracket and CD!="":CD = f"({CD})" 
    return CD
# %% 获取日期
def TDdate(start='2004-01-01',end='2023-01-01'):
    '''更新股市交易日'''
    import exchange_calendars as xcals
    xshg = xcals.get_calendar("XSHG")
    xshg_range = xshg.schedule.loc[start:end]
    return xshg_range.index.strftime("%Y-%m-%d").tolist()
def Holidays(start='2004-01-01',ToStr=True):
    '''获取节假日列表'''
    import chinese_calendar
    result = chinese_calendar.get_holidays(strTodate(start,"%Y-%m-%d"),strTodate(f'{str(ToDaydate())[:4]}-12-31',"%Y-%m-%d"))
    return [str(x) for x in result] if ToStr else  result

def CalendarMark(datelist):
    df = pd.DataFrame()
    df["TDday"] = datelist
    df["TDREF"] = df["TDday"].shift( 1)
    df["TDNext"]= df["TDday"].shift(-1)
    #--------------------------------------------------------------------------
    #拆解交易日
    df["Day"]  =df["TDday"].apply(lambda x:int(x[8:]))
    df["Month"]=df["TDday"].apply(lambda x:int(x[5:-3]))
    df["Year"] =df["TDday"].apply(lambda x:int(x[:4]))
    #--------------------------------------------------------------------------
    df["Mlast"]=np.where(df['Day']>df['Day'].shift(-1),1,0)
    df["TDday"]=pd.to_datetime(df["TDday"],format='%Y-%m-%d')
    df['XingQi'] =[i.weekday()+1 for i in df['TDday']]
    #--------------------------------------------------------------------------
    #交易日间隔时间
    df["dayspan"]=df["TDday"].shift(-1)-df["TDday"]
    df=df[:-1]#去尾
    df["dayspan"]=df["dayspan"].apply(lambda x:abs(int(str(x)[:-14]))-1)
    #--------------------------------------------------------------------------
    #下一交易日开盘时间
    df["Night"]=np.where(df["dayspan"]>2,0,np.where(df["dayspan"]>0,np.where(df['XingQi']<5,0,1),1))
    df["WeekNum"]=df["TDday"].apply(lambda x:x.isocalendar()[1])
    df["Wlast"]=np.where(df['XingQi']>4,1,np.where(df["Night"]<1,1,0))
    df["TDday"]=df["TDday"].astype("str")
    df["strtime"]=np.where(df["Night"]<1,"09:00:00","21:00:00")
    df["NextDay"]=np.where(df["Night"]<1,df["TDday"].shift(-1)+" "+df["strtime"],df["TDday"]+" "+df["strtime"])
    del df["strtime"]
    del df["dayspan"]
    #--------------------------------------------------------------------------
    #该月交易日有多少天
    df["Mdays"]=0
    for year in list(set(df["Year"].to_list())):
        dataY =df[df["Year"]==year].copy()
        for month in list(set(dataY["Month"].to_list())):
            dataM =dataY[dataY["Month"]==month]
            MDay=len(dataM)
            df["Mdays"]=np.where(df["Year"]==year,np.where(df["Month"]==month,MDay,df["Mdays"]),df["Mdays"])
    #--------------------------------------------------------------------------
    return df[1:-1]

def CalendarData(start='2004-01-01',end='2050-12-31'):
    '''交易日历'''
    df=pd.DataFrame()
    DateN=TDdate(start,end)
    #--------------------------------------------------------------------------
    Holiday = Holidays(start )
    #当前交易日前后
    df["TDday"] =DateN
    #删除错误交易日
    df["error"] =df["TDday"] .apply(lambda x:True if x in  Holiday else False)
    df.drop(df[df["error"]==True].index,inplace=True)
    del df["error"]
    return CalendarMark(df)
#%% IC IR 
def IC(a,b):
    s1=Series(a) #转为series类型
    s2=Series(b) #转为series类型
    corr=s1.corr(s2) #计算相关系数
    return corr
def IR(ICs):
    mean=sum(ICs)/len(ICs)
    ICstd1,ICstd2=STD(ICs)
    return mean/ICstd1
#%% 标准差
def STD(arr):
    arr_std_1 = np.std(arr, ddof=0)#总体标准差
    arr_std_2 = np.std(arr, ddof=1)#样本标准差
    return arr_std_1,arr_std_2
#%% 数字文字单位互转
def AutoSci(num):
    '''万计数'''
    return f"{round(num/1e4,3)}万" if num>1e4 else str(round(num,3))
def UnitChange(arge,str_num=False):
    '''万亿转数字'''
    def strofsize(arge, level):
        if level >= 2:
            return arge, level
        elif arge >= 10000:
            arge /= 10000
            level += 1
            return strofsize(arge, level)
        else:
            return arge, level
    if str_num:
        arge=str(arge)
        idxOfYi = arge.find('亿')
        idxOfWan = arge.find('万')
        if idxOfYi != -1 and idxOfWan != -1:
            return int(float(arge[:idxOfYi])*1e8 + float(arge[idxOfYi+1:idxOfWan])*1e4)
        elif idxOfYi != -1 and idxOfWan == -1:
            return int(float(arge[:idxOfYi])*1e8)
        elif idxOfYi == -1 and idxOfWan != -1:
            return int(float(arge[idxOfYi+1:idxOfWan])*1e4)
        elif idxOfYi == -1 and idxOfWan == -1:
            return float(arge)
    else:
        units = ['', '万', '亿']
        arge, level = strofsize(arge, 0)
        if level > len(units):
            level -= 1
        return '{}{}'.format(round(arge, 3), units[level])
#%% 菲波纳契
def FiBoNaCCi(n):
    '''斐波那契点位'''
    N=int((np.matrix([[1, 1], [1, 0]])**(n - 1)*np.matrix([[1],[0]]))[0,0])
    return N if N>=0 else None
def PosFBNCci(N,inis=0.1):
    '''斐波那契仓位'''
    return [inis+FiBoNaCCi(i)/100 for i in range(N)]
def PosListFB(N,inis=0.1):
    '''斐波那契数列仓位'''
    POSX=PosFBNCci(N,inis)
    BASP,SLIP,POS=100,[],[0,]
    for i in POSX:
        x=i*BASP
        BASP=BASP-x
        SLIP.append(x)
        POS.append(sum(SLIP)/100)
    return POS
def MADING(N):
    '''马丁仓位'''
    VOL,VOS=1,[1,]
    for i in range(1,N):
        VOL=VOL*2
        VOS.append(VOL)
    SUM=sum(VOS)
    POS=[i/SUM for i in VOS]
    return POS,VOS
#%% 运行时间
def run_time(func):
    '''
    装饰函数程序运行时长
    该函数不可以装饰多进程主函数
    '''
    def inner(*arg,**kwarg):
        s_time = time.time()
        res = func(*arg,**kwarg)
        e_time = time.time()
        log.Info(f'||运行耗时:{round(e_time - s_time,3)}秒||')
        return res
    return inner
def Interact():
    """
    执行后进入repl模式
    定义了一个名为interact的函数，用于进入REPL（Read-Eval-Print Loop）模式。
    REPL模式是一种交互式的编程环境，允许用户输入代码并立即执行并查看结果。
    在这个函数中，使用了Python的code模块中的InteractiveConsole类来创建一个REPL环境。
    当调用interact函数时，它会打开一个REPL会话，
    并将当前的全局变量作为环境变量传递给InteractiveConsole对象。
    这意味着在REPL会话中，你可以直接使用定义在全局作用域中的变量和函数。
    这个函数通常用于调试或快速探索代码的功能。
    你可以在REPL模式下输入代码并立即查看执行结果，这对于快速测试、调试和探索代码非常有用。
    """
    import code
    code.InteractiveConsole(locals=globals()).interact()


#%% 终结
if __name__ == '__main__':
    print("Formulae")
#//////////////////////////////////////////////////////////////////////////////





















