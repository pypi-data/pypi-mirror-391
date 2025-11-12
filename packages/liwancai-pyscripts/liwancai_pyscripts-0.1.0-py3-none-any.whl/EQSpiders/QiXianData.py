# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 17:32:43 2019
Created on Python3.6.8
@author:
    liwancai
    QQ:248411282
"""

import random
import pandas                          as pd
from PyScripts.Functions.LOG           import log
from datetime                          import datetime
from PyScripts.EQDBLinks.DBMySQL       import InitSqlDB
from PyScripts.EQDBLinks.GetFromDB     import Tbl_EQ_Calendar_data
from PyScripts.Functions.Formulae      import delint,get_strtime,DifEntSet,OnlyCHN,SetList,Sleep
################################################################################
def GetCode(x):
    '''根据名称更新code'''
    try:
        CODEBASE={ '铜': 'CU', '螺纹钢': 'RB', '锌': 'ZN', '铝': 'AL', '黄金': 'AU',
                   '线材': 'WR', '燃料油': 'FU', '天然橡胶': 'RU', '铅': 'PB', '白银': 'AG',
                   '石油沥青': 'BU', '热轧卷板': 'HC', '镍': 'NI', '锡': 'SN', '纸浆': 'SP',
                   '不锈钢': 'SS', 'PTA': 'TA', '白糖': 'SR', '棉花': 'CF', '普麦': 'PM',
                   '菜籽油': 'OI', '强麦': 'WH', '玻璃': 'FG', '菜籽粕': 'RM', '油菜籽': 'OI',
                   '硅铁': 'SF', '锰硅': 'SM', '甲醇': 'MA', '棉纱': 'CY', '尿素': 'UR',
                   '纯碱': 'SA', '涤纶短纤': 'PF', '棕榈油': 'P', '聚氯乙烯': 'V', '聚乙烯': 'L',
                   '豆一': 'A', '豆粕': 'M', '豆油': 'Y', '玉米': 'C', '铁矿石': 'I',
                   '鸡蛋': 'JD', '聚丙烯': 'PP', '玉米淀粉': 'CS', '乙二醇': 'EG',
                   '苯乙烯': 'EB', '液化石油气': 'PG', '生猪': 'LH', '红枣': 'CJ', 
                   '纤维板': 'FB', '粳米': 'RR', '早籼': 'RI', '低硫油': 'LU',
                   '沪镍': 'NI', '苹果': 'AP', '焦炭': 'J', '菜籽': 'RS',
                   '胶合板': 'BB', '中千股指': 'IM', '工业硅': 'SI', '二债': 'TS', 
                   '五债': 'TF', '焦煤': 'JM', '晚籼': 'LR', '国际铜': 'BC',
                   '上证股指': 'IH', '沪深加权': 'IF', '原油': 'SC', '动力煤': 'ZC',
                   '豆二': 'B', '花生': 'PK', '十债': 'T', '中证股指': 'IC', 
                   '粳稻': 'JR', '20号胶': 'NR'}
        return CODEBASE[x] 
    except:return x   
def FlashName(x):
    CHN=OnlyCHN(x)
    return CHN if len(CHN)>0 else x
    
def HBdata(data):
    '''拆分合并数据单元'''
    alldf=[data[i].columns.to_list() for i in range(len(data))][2:-1]
    最近合约=alldf[::2]
    主力合约=alldf[1::2]
    最近合约基差,最近合约基差P=[x[0] for x in 最近合约],[f"{float(x[1][:-1])}" for x in 最近合约]
    主力合约基差,主力合约基差P=[x[0] for x in 主力合约],[f"{float(x[1][:-1])}" for x in 主力合约]
    return  最近合约基差,最近合约基差P,主力合约基差,主力合约基差P
################################################################################
def GetData(date="2022-11-08"):
    '''获取期现数据'''
    log.Info(f"获取数据{date}")
    ############################################################################
    url=f"http://www.100ppi.com/sf/day-{date}.html"
    log.Info(f"爬取{date}的目标网址:\n {url}")
    try:
        #######################################################################
        ###获取数据
        data=pd.read_html(url, encoding='utf-8',header=0)
        if len(data)==0: return pd.DataFrame()
        df=data[1]#数据集
        #######################################################################
        ###修正表格字段名
        columns=df.columns
        columns=[f"{delint(columns[i][:4])}_{delint(df[columns[i]].iloc[0])}" for i in range(len(columns))]
        df.columns=columns
        log.Info(f"||获取数据成功\n|数据表头:|{columns}|")
        #######################################################################
        ###数据清洗
        log.Info("数据整理清洗...")
        for i in range(len(columns)):
            df[columns[i]]=df[columns[i]].apply(lambda x:None if x in columns[i] or "交易所"in x else x)
        df.dropna(axis=0,inplace=True) 
        xcolumns=data[0].columns
        df1=data[0]
        strs=""
        for x in range(len(xcolumns)):strs+=f"{df1[xcolumns[x]].iloc[0]}"
        #######################################################################
        date=get_strtime(strs)
        df["日期"]=f"{date}:00"
        df.rename(columns={"商品_商品":"商品"},inplace=True)
        df["商品"]=df["商品"].apply(lambda x:FlashName(x))
        df["code"]=df["商品"].apply(lambda x:GetCode(x))
        #######################################################################
        del df[columns[4]]
        del df[columns[7]]
        df[f"{columns[4]}"],df[f"{columns[4]}%"],df[f"{columns[7]}"],df[f"{columns[7]}%"]=HBdata(data)#处理合并单元格数据
        #######################################################################
        df[f"{columns[4]}"]=df[f"{columns[4]}"].astype('float')
        df[f"{columns[4]}%"]=df[f"{columns[4]}%"].astype('float')
        df[f"{columns[7]}"]=df[f"{columns[7]}"].astype('float')
        df[f"{columns[7]}%"]=df[f"{columns[7]}%"].astype('float')
        #######################################################################
        for key in ["最近合约_代码","主力合约_代码"]:
            df[key]=df[key].apply(lambda x:x.replace(delint(x),""))
        log.Info("数据整理清洗完成。")
        return df
    except Exception as exception:
        log.Error(str(exception))
        return pd.DataFrame()

################################################################################ 
def SqlDate(lcdb,dbname ="qh_baseinfo" ,tblname="tbl_QiXian_Data"):
    try:
        string=f"select {dbname}.{tblname}.日期 from {dbname}.{tblname} "
        dates=lcdb.GetData(string)["日期"].to_list()#获取数据
        log.Info("获取历史期现表中所有日期")
        return  dates
    except Exception as exception:log.Error(str(exception))
def SaveQXData(lcdb,dateday,dbname ="qh_baseinfo" ,tblname="tbl_QiXian_Data"):
    try:
        datas=GetData(dateday)
        if len(datas)==0: return
        datas.sort_values(by=['主力合约_现期差%'],ascending=True,inplace=True)
        datas.index=[i for i in range(len(datas))]
        ###ToSql################################################################
        savesqls=lcdb.SaveDF(datas,tblname,dbname= dbname)
        rst = lcdb.RunSql(savesqls)#运行保存sql
        if isinstance(rst,bool):log.Info(f"||保存{dateday}期现表数据成功|")
        else:log.Info(f"||保存{dateday}期现表数据失败|错误:|{rst}")
        lcdb.Commit()#事务提交
    except Exception as exception:log.Error(str(exception))
def SleepHQ():
    slptime=int(240*random.random())+30
    log.Info(f"随机sleep时间: {slptime}")
    Sleep(slptime)
def SaveAllQXData(lcdb,dbname ="qh_baseinfo" ,tblname="tbl_QiXian_Data"):
    ###获取已有数据的日期列表
    QXdates=SqlDate(lcdb,dbname ,tblname)
    if QXdates==None : QXdates=[]
    else:QXdates=[str(x) for x in QXdates]
    try:
        #######################################################################
        ###判断需要爬取数据的日期
        log.Info("判断数据获取需更日期")
        needdates=SetList(  Tbl_EQ_Calendar_data(
                lcdb,stime='2013-01-04',etime=str(datetime.now())[:19],
                select=["TDday"],limit=None,rstdf=True,defultlimit=None)["TDday"].to_list())
        needdates=DifEntSet(needdates,QXdates)#获取日期差集
        needdates.sort(reverse=True)#日期反排序
        log.Info("生成数据获取日期范围")
        #######################################################################
        ###遍历日期获取数据并保存数据
        for i in range(len(needdates)):
            dateday=needdates[i]
            log.Info(f"||爬取期现表数据：{dateday}|")
            if i%3==0:SleepHQ()
            try:SaveQXData(lcdb,dateday,dbname ,tblname)
            except Exception as exception:
                log.Error(str(exception))
                continue
    except Exception as exception:log.Error(str(exception))
################################################################################
if __name__ == '__main__':
    from PyScripts.Functions.LOG           import log
    from PyScripts.Functions.DirsFile      import ReadToml
    from PyScripts.EQUseApi.ApiBase        import SetUseapi
    from PyScripts.EQDBLinks.DBMySQL       import InitSqlDB
    config   = ReadToml("config",path="./Datas/etc/")
    lcdb = InitSqlDB(config,"cfg_177")
    SaveAllQXData(lcdb)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


