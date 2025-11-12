# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 20:07:00 2019
Created on Python3.6.8
@author:liwancai
    QQ:248411282
    Tel:13199701121
"""
#%%加载包
from PyScripts.Functions.Formulae      import HLV,ATR
#%% 海龟策略
class HaiGuiBS_001:
    '''
    海龟策略
    入场:N周期的最高价,最低价被突破,买1个UnitB
    加仓:每上涨0.5ATR加仓一个UnitB
    离场:反向破半周期高低价|或者破2ATR
    其他:UnitB等于初始净值的1%(去杠杆)对应一个ATR波动
    '''
    def __init__(self):
        '''初始化'''
        self.HLXY    =[HLV() for i in range(4)]                #初始化高低函数
        self.RUNM    ={"ls":0,"lsB":0,"REFlsB":0,"lsBNP":0,"REFlsBNP":0,"UnitB":0,"PriceB":0,
                       "lsS":0,"REFlsS":0,"lsSNP":0,"REFlsSNP":0,"UnitS":0,"PriceS":0,
                       "REFBH":0,"REFBL":0,"REFSL":0,"REFSH":0}#状态记录
        self.ATR     =ATR()                                    ###波动率
    def input(self,KLINE,argeM=10,argeH=21,argeL=21,promotion=1,M0=20,arge=20,N=2):
        '''
        输入参数
        ###案例:此输入为日线级别输入↓
        ###说明:一般采用大周期算参考线,小周期做加减仓或触发机制
        '''
        ###计算通道
        self.HLXY[0].input(KLINE.low ,arge=argeM) #做多回档中线
        self.HLXY[1].input(KLINE.high,arge=argeH) #突破高做多
        self.HLXY[2].input(KLINE.low ,arge=argeL) #突破低做空   
        self.HLXY[3].input(KLINE.high ,arge=argeM)#做空回档中线
        ###计算ATR
        self.ATR.input(KLINE,promotion,M0,arge,N)
    def SinGLE(self,kline,Unit:int):
        '''
        策略信号
        ###案例:此输入为分钟级别输入
        ###说明:一般采用大周期算参考线,小周期做加减仓或触发机制
        '''
        self.BLS(kline,Unit)#
        self.SLS(kline,Unit)#
        ###////////////////////////////////////////////////////////////////////
    def BLS(self,kline,Unit:int):
        '''多判断'''
        ###多头空仓且最新价创上周期新高↓
        if (self.RUNM["lsB"] ==0)&(kline.close>=self.RUNM["REFBH"]):
            self.RUNM["lsB"] ,self.RUNM["UnitB"] ,self.RUNM["lsBNP"],self.RUNM["PriceB"]=Unit,1,0.01,kline.close
        ###多头持仓并且价格新高0.5个ATR,且未加满N个unit
        elif (self.RUNM["lsB"] != 0)&((kline.close-self.RUNM["PriceB"])>0.5*self.ATR.atr)&(self.RUNM["UnitB"]<4):
            self.RUNM["UnitB"] += 1          #加仓次数
            self.RUNM["lsBNP"] += 0.01       #买卖百分比
            self.RUNM["lsB"]   += Unit       #买卖单位数量
            self.RUNM["PriceB"] = kline.close#买卖价格
        elif (self.RUNM["lsB"] != 0)&(kline.close<self.RUNM["REFBL"])|(kline.close<self.ATR.HBS):
            ###如果下破中线,或者下破2个ATR
            self.RUNM["lsB"]   = 0
            self.RUNM["lsBNP"] = 0
            self.RUNM["UnitB"] = 0
            self.RUNM["PriceB"]= kline.close
        ###////////////////////////////////////////////////////////////////////
    def SLS(self,kline,Unit:int):
        '''空判断'''
        ###空头空仓且最新价创上周期新低↓
        if (self.RUNM["lsS"] ==0)&(kline.close<=self.RUNM["REFSL"]):
            self.RUNM["lsS"] ,self.RUNM["UnitS"] ,self.RUNM["lsSNP"],self.RUNM["PriceS"]=-Unit,-1,-0.01,kline.close
        ###多头持仓并且价格新高0.5个ATR,且未加满N个unit
        elif (self.RUNM["lsS"] != 0)&(-1*(kline.close-self.RUNM["PriceS"])>0.5*self.ATR.atr)&(self.RUNM["UnitS"]>-4):
            self.RUNM["UnitS"] -= 1           #加仓次数
            self.RUNM["lsSNP"] -= 0.01        #买卖百分比
            self.RUNM["lsS"]   -= Unit        #买卖单位数量
            self.RUNM["PriceS"] = kline.close #买卖价格
        elif (self.RUNM["lsS"] !=0)&(kline.close>self.RUNM["REFSH"])|(kline.close>self.ATR.LBS):
            ###如果下破中线,或者下破2个ATR
            self.RUNM["lsS"]   = 0
            self.RUNM["lsSNP"] = 0
            self.RUNM["UnitS"] = 0
            self.RUNM["PriceS"]= kline.close
        ###////////////////////////////////////////////////////////////////////
    def ReCode(self):
        '''后置记录'''
        self.RUNM["REFBH"],self.RUNM["REFBL"]=self.HLXY[1].H,self.HLXY[0].L
        self.RUNM["REFSL"],self.RUNM["REFSH"]=self.HLXY[2].L,self.HLXY[3].H
        ###////////////////////////////////////////////////////////////////////
