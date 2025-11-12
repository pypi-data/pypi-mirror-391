# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 20:07:00 2019
Created on Python3.6.8
@author:liwancai
    QQ:248411282
    Tel:13199701121
"""
#%%加载包
from liwancai.Functions.Formulae      import MACD,SKDJ,CLS
##############################################################################################################################################################
#%% MacdSKDJ标记
class MarkMacdSKDJ:
    '''
    行情数据分级标记基础模块
    用于生成专属组合行情数据
    '''
    def __init__(self):
        '''要素初始化'''
        self.MACDS  = [MACD() for i in range(8)]
        self.SKDJS  = [SKDJ() for i in range(8)]
        self.Rancour= CLS({"UP":[0]*8,"DW":[0]*8})
        self.Crisis = [CLS({"ActTO":0,"REFActTO":0,"energy":CLS({"UP":0,"DW":0}), "expand":0,"BatonID":0}) for i in range(6)]
    def input(self,kline):
        '''数据输入'''
        price = kline.close
        #############################################################################
        ###小级别76 54 32 10 |1,2,5,10,25,50,125,250
        self.MACDS[0].input(price, promotion=1, e12=12, e26=26, e9=9,sl=False,limit=1)
        self.MACDS[1].input(price, promotion=2, e12=12, e26=26, e9=9,sl=False,limit=1)
        ###中级别
        self.MACDS[2].input(price, promotion=5, e12=12, e26=26, e9=9,sl=False,limit=3)
        self.MACDS[3].input(price, promotion=10, e12=12, e26=26, e9=9,sl=False,limit=4)
        ###主机别
        self.MACDS[4].input(price, promotion=25, e12=12, e26=26, e9=9,sl=False,limit=5)
        self.MACDS[5].input(price, promotion=50, e12=12, e26=26, e9=9,sl=False,limit=6)
        ###大级别
        self.MACDS[6].input(price, promotion=125, e12=12, e26=26, e9=9,sl=False,limit=7)
        self.MACDS[7].input(price, promotion=250, e12=12, e26=26, e9=9,sl=False,limit=8)
        #############################################################################
        ###小级别76 54 32 10 |6:2 12:7 21:7 45:15 120:40 210:70 450:150 1200:400|
        self.SKDJS[0].input(kline, N= 6, M= 2)
        self.SKDJS[1].input(kline, N=12, M= 4)
        ###中级别
        self.SKDJS[2].input(kline, N=21, M= 7)
        self.SKDJS[3].input(kline, N=45, M=15)
        ###主级别
        self.SKDJS[4].input(kline, N=120, M=40)
        self.SKDJS[5].input(kline, N=210, M=70)
        ###大级别
        self.SKDJS[6].input(kline, N=450 , M=150)
        self.SKDJS[7].input(kline, N=1200, M=400)
        #############################################################################
    def DWMACD(self,i):
        '''柱子方向'''
        return self.MACDS[i].macd/abs(self.MACDS[i].macd)if self.MACDS[i].macd!=0 else 0
    def ABCD(self,i,ACD=[1,3,-4,-2]):
        '''ABCD属性'''
        return self.DWMACD(i)*self.MACDS[i].stats in ACD
    def NewID(self,i,kline):
        '''
        放于ActTO函数之后
        记录趋势传递ID
        '''
        if self.Crisis[i].ActTO != self.Crisis[i].REFActTO:
            ###如果是初始就给予初始编号否则就继承编号###
            if i<2:self.Crisis[i].BatonID=f"ID{i}_TO{self.Crisis[i].ActTO}_{kline.kid}"
            else:self.Crisis[i].BatonID=self.Crisis[i-1].BatonID
        self.Crisis[i].REFActTO=self.Crisis[i].ActTO
    def SINMACD(self,i,kline):
        '''Macd标记'''
        UP=self.ABCD(i-1,ACD=[1,3,-4,-2]) and self.ABCD(i,ACD=[1,3,-4,-2])and self.ABCD(i+1,ACD=[1,3,-4,-2]) 
        DW=self.ABCD(i-1,ACD=[-1,-3,4,2]) and self.ABCD(i,ACD=[-1,-3,4,2])and self.ABCD(i+1,ACD=[-1,-3,4,2]) 
        if UP:self.Crisis[i].ActTO = 1
        if DW:self.Crisis[i].ActTO =-1
        self.NewID(i,kline)
        self.Energy(i)
    def Energy(self,i):
        '''能量传递1'''
        self.Crisis[i].energy.UP = ((100-self.SKDJS[i-1].SumP.UP)+self.SKDJS[i].SumP.UP+self.SKDJS[i+1].SumP.UP)/3
        self.Crisis[i].energy.DW = ((100-self.SKDJS[i-1].SumP.DW)+self.SKDJS[i].SumP.DW+self.SKDJS[i+1].SumP.DW)/3
    def SINSKDJ(self,i):
        '''能量传递2'''
        self.Rancour.UP[i]=self.SKDJS[i].SumP.UP
        self.Rancour.DW[i]=self.SKDJS[i].SumP.DW
    def SinGLE(self,kline,Unit=1):
        '''序列计算'''
        for i in range(8):self.SINSKDJ(i)
        for i in range(1,6):self.SINMACD(i,kline)
##############################################################################################################################################################
















































