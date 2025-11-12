# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 17:32:43 2019
Created on Python3.6.8
@author:
    liwancai
    QQ:248411282
"""
from liwancai.Functions.LOG        import log
from datetime                       import datetime,timedelta
from liwancai.Functions.Formulae   import RoundUp,SetList,DfToType,delpunc,LinkSelect,DF_to_Json,ToDaydate,strTodate,ToDaytime,strTotime,run_time
#%% 基础函数
#%% MySql查询
@run_time
def Tbl_EQ_GetSQLData(lcdb,string,dbname="",TimeToStr=["update_time"],rstdf=False):
    '''
    获取数据库数据【不可直接暴露于数据接口】
    '''
    try:
        lcdb.UseDB(dbname)
        log.Info(f"\n||SQL语句:\n{string}")
        df=lcdb.GetData(string)#获取数据
        if len(df)<1 : return df if rstdf else []#空数据返回
        DfToType(df,TimeToStr)#修改列的数据格式
        return df  if rstdf else DF_to_Json(df) 
    except Exception as exception:
        errmsg = f"||获取数据库数据出错:|{str(exception)}|"
        log.Error(errmsg)
        return errmsg
#%% 时间范围查询
    ###TimeRange数据表相关小工具###
def TODATE(x:list):
    '''时间拼接'''
    return [f"{ToDaydate()} {i}" for i in x]
def Cot1Min(x:list,NUM=1):
    '''减分钟'''
    return [((strTodate(i)-timedelta(minutes =NUM)).strftime('%Y-%m-%d %H:%M:%S'))[-8:] for i in x]
def Uop1Min(x:list,NUM=1):
    '''加分钟'''
    return [((strTodate(i)+timedelta(minutes =NUM)).strftime('%Y-%m-%d %H:%M:%S'))[-8:] for i in x]
def TOTIME(x:list):
    '''时刻对应时间戳'''
    return [float(f"{strTotime(i)-ToDaytime()}") for i in x]  
def ListTo(x):
    '''df[key]==>>list'''
    return f"{x[0][-8:]},{x[1][-8:]},{x[2][-8:]},{x[3][-8:]}"
def TointTime(df,ToInt:bool=True):
    '''将时间转化为时间戳'''
    keys=['closestart', 'closetimes', 'opentimes', 'openstart','closeend']
    for key in keys : df[key]=df[key].apply(lambda x:x.split(","))#分离
    if not ToInt : return df
    for key in keys: #转时间戳
        df[key]=df[key].apply(lambda x:   TODATE(x))#
        df[key]=df[key].apply(lambda x:   TOTIME(x))#
    return df
@run_time
def Tbl_EQ_Time_Range(lcdb,Breed:list=[],ToInt:bool=True,rstdf=False,whereCD=""):
    '''获取品种时间范围'''
    try:
        ##########################################################################################
        if len(Breed)<1:CDbreed = "" 
        else:
            CDbreed = [f"Breed='{x}'" for x in Breed]#条件列表
            CDbreed = LinkSelect(CDbreed,CD='',link=" or ")#条件拼接
        ##########################################################################################
        if whereCD!='':whereCD =f"where {CDbreed}"
        string=f"select * from BaseData.tbl_time_range {whereCD} "
        log.Info(f"\n||获取品种时间范围||SQL语句:\n{string}")
        df = lcdb.GetData(string,True)#获取数据
        if len(df)<1 : return df if rstdf else []#空数据返回
        df["ks1span"] = df["ks1span"].apply(lambda x:x.split(","))
        DfToType(df,["update_time","TDday"] )#修改列的数据格式
        TointTime(df,ToInt) 
        if rstdf : return df
        return DF_to_Json(df)[0] if len(df)==1 else {x["Breed"]:x for x in DF_to_Json(df)}
    except Exception as exception:
        err_msg=f"||获取品种时间范围|错误:|{Breed}_{ToInt}_{rstdf}_{str(exception)}|"
        log.Error(err_msg)
        return err_msg
    #%% 交易日历查询 
def DateTDDay(QHC,dt):
    ''' 
    需先获取交易日历
    返回日期下对应的交易日
    QHC交易日dict信息
    返回指定自然日时间对应的交易日时间
    '''
    try:
        cond0=(strTodate(dt)).hour>16 and strTodate(dt).weekday()<5
        return QHC["TDNext"] if cond0  else QHC["TDday"]
    except Exception as exception: log.Error(str(exception))
###############################################################################
@run_time
def Tbl_EQ_Calendar_data(lcdb,stime="",etime="",limit=1,TDFiled:str="TDday",select:list=[],rstdf:bool=False,left=True,defultlimit=10000,Timelimit=True):
    """
    从指定的数据库表中检索日历数据。
    """
    try:
        dbname   = "EQ_BaseData"
        tblname  = "tbl_trade_dates"
        ESTimeCDs= ESTimeCDLink(stime,etime,dbname,tblname,TDFiled,left=left)
        esTimeCD = LinkSelect(ESTimeCDs,"","and")#条件拼接
        limitCD  = NewLimit(limit,stime,etime,defult=defultlimit,Timelimit=Timelimit)
        selectCD = NewSelect(select ,dbname ,tblname )
        WhereCD  = f"where {esTimeCD}"    if esTimeCD!=""    else ""
        ###===================================================================================
        string= F"SELECT {selectCD} FROM {DBTBLLink(dbname,tblname,False)}  {WhereCD} {limitCD} ;"
        log.Info(f"\n||获取交易日历数据||SQL语句:\n{string}")
        df=lcdb.GetData(string,True)#获取数据
        if len(df)<1 : return df if rstdf else []#空数据返回
        DfToType(df,["update_time","TDday","NextDay","TDNext","TDREF"])#修改列的数据格式
        return df  if rstdf else DF_to_Json(df) 
    except Exception as exception:
        err_msg=f"||交易日历数据获取错误:|stime:|{stime}|etime:|{etime}|TDFiled:|{TDFiled}|错误:|{str(exception)}|"
        log.Error(err_msg)
        return err_msg
###############################################################################
@run_time
def Tbl_EQ_NowTDday(lcdb):
    '''当前交易日'''
    try:
        TDDateData = Tbl_EQ_Calendar_data(lcdb,stime=str(datetime.now())[:10])[0]#注意这里只取日期做数据检索
        return DateTDDay( TDDateData ,datetime.now() )#当日实时交易日返回
    except Exception as exception:
        err_msg=f"||获取当前交易日数据错误:|{str(exception)}|"
        log.Error(err_msg)
        return err_msg
    #%% 批量连接数据库名表名字段名
def DBTblFileds(dbname:str,tblname:str,fileds:list=[]):
    '''
    返回一个列表，其中包含所给定数据库中指定表的指定字段的格式化字符串。
    :param dbname: 表示数据库名称的字符串。
    :param tblname: 表示表名称的字符串。
    :param fileds: 一个字符串列表，表示要包含在返回列表中的字段。默认为空列表。
    :return: 包含给定数据库中给定表的指定字段的格式化字符串的列表。如果未指定字段，则返回所有字段。
    数据库，数据表，字段的连接列表
    ['dbname.tblname.close', 'dbname.tblname.period', 'dbname.tblname.code', 'dbname.tblname.trade_date']
    '''
    return [f"{dbname}.{tblname}.{x}" for x in fileds ] if len(fileds)>0 else [f"{dbname}.{tblname}.*" ]
    #%% 多表条件联接(内外连接)
def LinkDBWith(dbA:str,dbB:str,tblA:str,tblB:str,CDFileds,method:str="INNER JOIN",linkwith="and"):
    ''' 
    基于一个公共字段，将来自不同数据库的两个表链接起来。

    :param dbA: 第一个数据库的名称。
    :type dbA: str
    :param dbB: 第二个数据库的名称。
    :type dbB: str
    :param tblA: 要从第一个数据库链接的表的名称。
    :type tblA: str
    :param tblB: 要从第二个数据库链接的表的名称。
    :type tblB: str
    :param CDFiled: 公共字段的名称。
    :type CDFiled: str
    :param method: 要执行的连接类型。默认为 'INNER JOIN'。
    :type method: str
    :return: 表示链接两个表的 SQL 查询的字符串。
    :rtype: str
    表连接条件查询
    INNER JOIN dbA.tblA ON dbA.tblA.CDFiled=dbB.tblB.CDFiled 
    '''
    if isinstance(CDFileds,list): condiction = LinkSelect([ f" {dbA}.{tblA}.{CDFiled}={dbB}.{tblB}.{CDFiled} " for CDFiled in CDFileds ],"",linkwith,False)
    else: condiction = f" {dbA}.{tblA}.{CDFileds}={dbB}.{tblB}.{CDFileds} "
    return f"{method} {dbA}.{tblA} ON {condiction} "
    #%% 多表联合条件查询
def MultiLinkData(dbnames:list=[],GDB:list=[],tblnames:list=[],Gtbl:list=[],fileds:list=[],
                  CDFiled:list=[],method:list=["INNER JOIN"],whereCD:str="",limitCD:str=""):
    '''
    多表联合查询，对指定的一组表执行多表连接。
    :param dbnames: 数据库名称列表。
    :param GDB: 全局数据库名称。
    :param tblnames: 表名称列表。
    :param Gtbl: 全局表名称。
    :param fileds: 字段列表。
    :param CDFiled: 连接条件。
    :param method: 连接方法列表。
    :param whereCD: 连接条件文本。
    :return: SQL 查询字符串。
    ###====================================================================================================================
    timeselect = f"{dbname}.{tblname}.trade_time>'2023-01-01' and {dbname}.{tblname}.trade_time<'2023-06-09 16:11:49'"
    string = MultiLinkData(['gp_codefqyz','gp_codehqdb' ,'gp_codeksid'],['gp_codefqyz','gp_codehqdb'],
                  ['tbl_000001sz_all','tbl_000001sz_1440','tbl_000001sz_1440'],['tbl_000001sz_all','tbl_000001sz_1440'],
                  [['adj_factor','REFclose','hfq','qfq'],[],['kid']] ,['trade_date','trade_time'],
                  ["INNER JOIN","LEFT JOIN"],timeselect)
    SELECT
        gp_codefqyz.tbl_000001sz_all.adj_factor,
        gp_codefqyz.tbl_000001sz_all.REFclose,
        gp_codefqyz.tbl_000001sz_all.hfq,
        gp_codefqyz.tbl_000001sz_all.qfq,
        gp_codehqdb.tbl_000001sz_1440.*,
        gp_codeksid.tbl_000001sz_1440.kid 
    FROM
        gp_codefqyz.tbl_000001sz_all
        INNER JOIN gp_codehqdb.tbl_000001sz_1440 ON gp_codehqdb.tbl_000001sz_1440.trade_date = gp_codefqyz.tbl_000001sz_all.trade_date
        LEFT JOIN gp_codeksid.tbl_000001sz_1440 ON gp_codeksid.tbl_000001sz_1440.trade_time = gp_codehqdb.tbl_000001sz_1440.trade_time 
    WHERE
        gp_codehqdb.tbl_000001sz_1440.trade_time > '2023-01-01' 
        AND gp_codehqdb.tbl_000001sz_1440.trade_time < '2023-06-09 16:11:49';
    ###====================================================================================================================
    dbname  ="gp_dayshqdb"
    tblname ="tbl_20230531_1440"
    codeselect = LinkSelect([f"{dbname}.{tblname}.code='{x}'" for x in  Kiddata["code"].to_list()],"")
    string     = MultiLinkData(['gp_daysfqyz','gp_dayshqdb' ,'gp_daysksid'],['gp_daysfqyz','gp_dayshqdb'],
                  ['tbl_20230531_all','tbl_20230531_1440','tbl_20230531_1440'],['tbl_20230531_all','tbl_20230531_1440'],
                  [['adj_factor','REFclose','hfq','qfq'],[],['kid']] ,[['code','trade_date'],['code','trade_time']],
                  ["INNER JOIN","LEFT JOIN"],codeselect)

    SELECT
        gp_daysfqyz.tbl_20230531_all.adj_factor,
        gp_daysfqyz.tbl_20230531_all.REFclose,
        gp_daysfqyz.tbl_20230531_all.hfq,
        gp_daysfqyz.tbl_20230531_all.qfq,
        gp_dayshqdb.tbl_20230531_1440.*,
        gp_daysksid.tbl_20230531_1440.kid 
    FROM
        gp_daysfqyz.tbl_20230531_all
        INNER JOIN gp_dayshqdb.tbl_20230531_1440 ON gp_dayshqdb.tbl_20230531_1440.CODE = gp_daysfqyz.tbl_20230531_all.CODE 
        AND gp_dayshqdb.tbl_20230531_1440.trade_date = gp_daysfqyz.tbl_20230531_all.trade_date
        LEFT JOIN gp_daysksid.tbl_20230531_1440 ON gp_daysksid.tbl_20230531_1440.CODE = gp_dayshqdb.tbl_20230531_1440.CODE 
        AND gp_daysksid.tbl_20230531_1440.trade_time = gp_dayshqdb.tbl_20230531_1440.trade_time 
    WHERE
        ( gp_dayshqdb.tbl_20230531_1440.CODE = '000001.SZ' OR gp_dayshqdb.tbl_20230531_1440.CODE = '000002.SZ' );
    ###====================================================================================================================
    '''
    selects ,froms ,linkid =[],[],0
    for i in range(len(dbnames)):
        selects += DBTblFileds(dbnames[i],tblnames[i],fileds[i])
        if dbnames[i]== GDB[linkid] :continue
        froms.append(LinkDBWith(dbnames[i],GDB[linkid],tblnames[i],Gtbl[linkid],CDFiled[linkid],method=method[linkid]))#多表联合
        linkid+=1
    froms   = LinkSelect(froms,link=" ",bracket=False)#条件拼接  
    selects = LinkSelect(selects,link=",",bracket=False)#条件拼接
    where   = f"WHERE  ({whereCD}) " if  ('>' in whereCD) or ('<' in whereCD)  or ('=' in whereCD) else " WHERE volume>0 "
    string  = f"select {selects} FROM {GDB[0]}.{Gtbl[0]} {froms} {where} {limitCD};"
    return string

def ESTimeCDLink(stime,etime,dbfrom,tblfrom,RangeTime="trade_time",left=False):
    '''时间条件选择'''
    DBTBL = DBTBLLink(dbfrom,tblfrom)
    left  = "=" if left else ""
    CD1   = f"{DBTBL}{RangeTime}>{left}'{stime}'"  if stime!="" else ""#左不包含
    CD2   = f"{DBTBL}{RangeTime}<='{etime}'"  if etime!="" else ""#右包含
    CDs   = [x for x in [CD1,CD2] if x!=""] 
    return CDs
###############################################################################
def NewLimit(limit=None,stime:str="",etime:str="",defult=100,Timelimit=True):
    """
    基于给定的参数返回一个用于 SQL 查询的 limit 字符串。

    :param limit: 一个整数，表示要检索的最大项目数。默认为 None。
    :param stime: 一个字符串，表示开始时间。格式为 "YYYY-MM-DD"。默认为空字符串。
    :param etime: 一个字符串，表示结束时间。格式为 "YYYY-MM-DD"。默认为空字符串。
    :param defult: 一个整数，表示未指定时 limit 的默认值。默认为 100。
    :param Timelimit: 一个布尔值，表示是否应用基于时间的限制。默认为 True。
    :return: 一个字符串，表示用于 SQL 查询的 limit 子句。
    """
    if not limit : limit=defult
    if (stime!="" and etime!="" and Timelimit):limit=None
    limit =f" limit {limit} " if limit     else ""#数量限制
    return limit
###############################################################################
def DBTBLLink(dbfrom:str="",tblfrom:str="",Filed=True):
    if dbfrom  !="": dbfrom=f"{dbfrom}." 
    Filedadd= "." if Filed else ""
    if tblfrom !="":tblfrom=f"{tblfrom}{Filedadd}" 
    DBTBL  = f"{dbfrom}{tblfrom}" 
    return DBTBL
def NewSelect(select:list=[],dbfrom:str="",tblfrom:str=""):
    """
    创建一个 SELECT 语句，用于选择给定表和数据库中的特定列。
    :param select: 一个字符串列表，表示要选择的列名。默认为空列表。
    :param dbfrom: 一个字符串，表示数据库名称。默认为空字符串。
    :param tblfrom: 一个字符串，表示表名称。默认为空字符串。
    :return: 一个字符串，表示生成的 SELECT 语句。
    """
    DBTBL = DBTBLLink(dbfrom,tblfrom,True)
    select = delpunc(str([f"{DBTBL}{x}" for x in select]) ,"\'\[\]\"") if len(select)>0 else f"{DBTBL}*"
    return select
###########################################################################
#%% 获取股票指定日期的code列表
@run_time
def Tbl_GP_Codelist(lcdb,tradedate=ToDaydate('%Y%m%d')):
    if tradedate=="":tradedate=ToDaydate('%Y%m%d')
    tradedate=int(tradedate.replace("-",""))
    Tbls = lcdb.GetTbls("gp_daysksid")
    Tbls = [int(x.split("_")[1]) for x in Tbls]
    if tradedate not in Tbls:
        tradedate = max(Tbls)
    string = f"select code,kid from tbl_{tradedate}_1440 ;"
    df  = lcdb.GetData(string,True)
    return  {df["code"].iloc[i]:int(df["kid"].iloc[i])  for i in range(len(df))}#
@run_time
def Tbl_GP_DaysHQDB(lcdb,tradedate,period,codes=[],select=[],whereCD=""):
    tradedate=tradedate.replace("-","")
    tblname=f"tbl_{tradedate}_{period}"
    if len(codes)>0: whereCD +=sqlstrselectcode(codes).replace("where","").replace("code=",f"gp_dayshqdb.{tblname}.code=")
    dbnames     = ["gp_daysfqyz","gp_dayshqdb","gp_daysksid"]#数据库列表与表名一一对应
    GDB         = ["gp_daysfqyz","gp_dayshqdb"]#公共联合数据库
    tblnames    = [f"tbl_{tradedate}_all",tblname,tblname]#数据库对应的数据表
    Gtbl        = [f"tbl_{tradedate}_all",tblname]#公共联合数据表
    fileds      = [["hfq","qfq","adj_factor","REFclose"],select,["kid"]]#数据查询字段,与数据表一一对应
    CDFiled     = [["code","trade_date"],["code","trade_time"]]#公共数据库的公共联合表的条件连接字段
    method      = ["INNER JOIN","LEFT JOIN "]#表之间连接方式，与数据表顺序一一对应
    string      = MultiLinkData(dbnames,GDB,tblnames,Gtbl,fileds, CDFiled,method,whereCD)
    df  = lcdb.GetData(string,True)
    df.fillna(0,inplace=True)
    DfToType(df,["update_time","trade_time","trade_date"],"str")#修改列的数据格式
    return   df
#%% 股票个票行情数据
@run_time
def Tbl_GP_CodeHQDB(lcdb,code,period='1440',stime='',etime='',select=[],limit=0,page=0,pagesize=0,rstdf=False,left=False,defultlimit=10000,Timelimit=True,NullValue=0):
    """
    一个从数据库中检索股市数据的函数，它基于给定的参数。
    lcdb   ：数据库实例。
    code   ：要检索数据的股票代码。
    period ：要检索数据的时间段。
    stime  ：要检索数据的开始时间。
    etime  ：要检索数据的结束时间。
    select ：要从数据库中检索的数据字段。
    limit  ：要检索的最大数据点数。默认为0，表示没有限制。
    page   ：要检索的数据页。默认为0，表示检索所有数据。
    pagesize：每页要检索的数据点数。默认为0，表示在一页上检索所有数据。
    rstdf   ：一个布尔值，指示是否以dataframe（False）或JSON（True）的形式返回数据。默认为False。
    left    ：一个布尔值，指示是否使用左包含。默认为True。
    defultlimit：未指定limit时使用的默认限制。默认为100。

    返回一个包含股市数据的dataframe、可以用于显示数据的页数以及在数据库中找到的数据总数。
    """

    dbname      = "gp_codehqdb"
    Gfiled      = "trade_time"
    code        = code.replace('.','')
    tblname     = f"tbl_{code}_{period}"
    ###########################################################################
    ESTimeCDs   = ESTimeCDLink(stime,etime,dbname,tblname,RangeTime="trade_time",left=left)#时间条件
    whereCDs    = LinkSelect(ESTimeCDs,"","and")#条件拼接
    CDlimit     = NewLimit(limit,stime,etime,defult=defultlimit,Timelimit=Timelimit)
    WhereCD     = f"where {whereCDs}"   if ('>' in whereCDs) or ('<' in whereCDs)  or ('=' in whereCDs) else ""
    ###########################################################################
    string      = f"select count({Gfiled}) from {DBTBLLink(dbname,tblname,False)} {WhereCD} {CDlimit} ;" if page>0 and pagesize>0  else ""
    datanum     = lcdb.GetData(string,False)["data"][0][0] if page>0 and pagesize>0 else  0 #数据总量
    if etime!="" and stime==""  and datanum>limit and limit>0 : datanum = limit
    sumpage     = RoundUp(datanum/pagesize,0) if page>0 and pagesize>0 else  1 #分页页数
    if page>sumpage : page = sumpage
    pagelimit   = pagesize if pagesize >0  and sumpage>1 else limit
    if pagesize >0  and sumpage>1  : Timelimit   = False
    ###########################################################################
    CDlimit     = NewLimit(pagelimit,stime,etime,defult=defultlimit,Timelimit=Timelimit)
    OrderBy     = f" ORDER BY {DBTBLLink(dbname,tblname)}{Gfiled} desc " if etime!="" and stime=="" else f" ORDER BY {DBTBLLink(dbname,tblname)}{Gfiled} "
    LimitOFFSET = f" OFFSET {(page-1)*pagelimit}" if sumpage>1 else ""
    ###########################################################################
    whereCD     = f"{whereCDs}{OrderBy}"
    limitCD     = f"{CDlimit}{LimitOFFSET} "
    dbnames     = ["gp_codefqyz",dbname,"gp_codeksid"]#数据库列表与表名一一对应
    GDB         = ["gp_codefqyz","gp_codehqdb"]#公共联合数据库
    tblnames    = [f"tbl_{code}_all",tblname,tblname]#数据库对应的数据表
    Gtbl        = [f"tbl_{code}_all",tblname]#公共联合数据表
    fileds      = [["hfq","qfq","adj_factor","REFclose"],select,["kid"]]#数据查询字段,与数据表一一对应
    CDFiled     = ["trade_date","trade_time"]#公共数据库的公共联合表的条件连接字段
    method      = ["INNER JOIN","LEFT JOIN "]#表之间连接方式，与数据表顺序一一对应
    string      = MultiLinkData(dbnames,GDB,tblnames,Gtbl,fileds, CDFiled,method,whereCD,limitCD)
    ###########################################################################
    log.Info(f"\n||获取股票个票行情数据||SQL语句:\n{string}")
    df=lcdb.GetData(string,True)#获取数据
    df.fillna(NullValue,inplace=True)
    if etime!="" and stime=="" :df.sort_values(by=Gfiled,axis=0,ascending=True, inplace=True)
    DfToType(df,["update_time","trade_time","trade_date"])#修改列的数据格式
    dfnum = len(df)
    if not rstdf :df = DF_to_Json(df)
    if datanum<1 and dfnum>0:datanum=dfnum
    return df,sumpage,datanum
###############################################################################
#%% 获取K线ID
@run_time
def Tbl_GPQH_CodeKSID(lcdb,dbname,code,period,sortbyfiled= "trade_time",rstdf=True,
                      select =["trade_date","code","trade_time"]):
    """
    非接口调用版
    获取股票或期货K线的ID表
    生成一个 SQL 查询，以从数据库中的表中检索数据，并将数据作为 pandas 数据框返回。
    :param lcdb: 表示本地数据库连接的 LocalCodeDB 类的对象。
    :param dbname: 一个字符串，表示数据库的名称。
    :param code: 一个字符串，表示要从表中查询的代码。
    :param period: 一个字符串，表示要查询数据的时间周期。
    :param sortbyfiled: 一个字符串，表示按其对数据进行排序的字段。默认值为 "trade_time"。
    :param rstdf: 一个布尔值，表示结果是否应返回为 pandas 数据帧。默认值为 True。
    :param select: 一个字符串列表，表示要从表中选择的列。默认值为 ["trade_date","code","trade_time"]。
    :return: 包含查询数据的 pandas 数据帧。
    #----------------------------------------------------------------------------------------------------
    # string  = f"SELECT {select}  FROM {dbname}.{tblname} ORDER BY {dbname}.{tblname}.{sortbyfiled} ;"
    # df = lcdb.GetData(string,True)
    # df["kid"]=[i for i in range(len(df))]
    # return  df if rstdf else DF_to_Json(df)
    #----------------------------------------------------------------------------------------------------
    """
    tblname = f"tbl_{code.replace('.','')}_{period}"
    select  = NewSelect(select,dbname,tblname)
    string  = f"SELECT {select} ,( @kid := @kid + 1 ) AS kid FROM {dbname}.{tblname} , ( SELECT @kid := 0 ) AS oldkid   ORDER BY {dbname}.{tblname}.{sortbyfiled}  "
    log.Info(f"\n||获取股票或期货K线的ID表||SQL语句:\n{string}")
    return  lcdb.GetData(string,rstdf)
#%% 获取期现表数据
@run_time
def Tbl_QH_QiXianData(lcdb,Breed,SDate="",EDate="",limit=0,rstdf=False,left=False,defultlimit=10000,Timelimit=True):
    dbname   = "qh_baseinfo"
    tblname  = "tbl_qixian_data"
    BreedCDs = [f" code='{x}' " for x in Breed]
    BreedCDs = LinkSelect(BreedCDs,"","or")#条件拼接
    ESTimeCDs= ESTimeCDLink(SDate,EDate,dbname,tblname,RangeTime="日期",left=left)#时间条件
    ESTimeCDs= LinkSelect(ESTimeCDs,BreedCDs,"and")#条件拼接
    WhereCD  = f"where {ESTimeCDs}"    if ESTimeCDs!=""    else ""
    CDlimit  = NewLimit(limit,SDate,EDate,defult=defultlimit,Timelimit=Timelimit)
    string   = f"select * from {dbname}.{tblname} {WhereCD} {CDlimit}"
    log.Info(f"\n||获取期现表数据||SQL语句:\n{string}")
    df       =  lcdb.GetData(string,True)
    DfToType(df,["update_time","日期"])#修改列的数据格式
    return df  if rstdf else DF_to_Json(df) 
#%% 获取展示策略的日线曲线
@run_time
def Tbl_GP_BKHQ(lcdb,stime,etime,tblname):
    timeselect = f"gp_linesbases.{tblname}.trade_time>='{stime}' and gp_linesbases.{tblname}.trade_time<='{etime}'"
    Tbls =["tbl_xpdhqs0_1440","tbl_xpdhqs1_1440","tbl_xpqsdhhc0_1440","tbl_xpqsdhhc1_1440",
           "tbl_gwqsdhhc0_1440","tbl_gwqsdhhc1_1440","tbl_mtdhhc0_1440","tbl_mtdhhc1_1440",
           "tbl_qsdhhc0_1440","tbl_qsdhhc1_1440"]# 
    if tblname.lower() in Tbls:
        string = MultiLinkData(['gp_linesbases','gp_lineweights'  ],['gp_linesbases' ],
                    [tblname,tblname],[tblname],
                    [[], ["weight0","weight1","weight2","weight3","weight4","weight5","weight6"] ] ,['trade_time'],
                    ["INNER JOIN" ],timeselect)
    else:string=f"select * from gp_linesbases.{tblname} where {timeselect}"
    df  = lcdb.GetData(string,True)
    return  df
@run_time
def Tbl_GP_StockPool(lcdb,tradedate,bkhqname):
    tradedate = tradedate.replace("-","")[:8]
    strsql   = f"SELECT trade_date,trade_time,code,period  FROM gp_{bkhqname}.tbl_{tradedate}_1440 where CMV_Mark<3 and TMV_Mark<3 AND PB_Mark<3 and PE_Mark<3 AND FTR_Mark<4 and amount_Mark<3 "
    rst  = lcdb.GetData(strsql,True)
    return rst
@run_time
def Tbl_GP_MACDPool(lcdb,tradedate):
    tradedate = tradedate.replace("-","")[:8]
    classMACD="REFClassUnion"
    if tradedate>ToDaydate('%Y%m%d'):
        Tbls=lcdb.GetTbls("gp_daysksid")
        Tbls=sorted(list(set([Tbl.split("_")[1] for Tbl in Tbls if "1440" in Tbl])))
        tradedate=Tbls[-1]
        classMACD="ClassUnion"
    strsql   = f"SELECT trade_date,trade_time,code,period  FROM gp_daysclass.tbl_{tradedate}_1440 where FIND_IN_SET( '1', {classMACD} ) = 1 "
    rst  = lcdb.GetData(strsql,True)
    return rst
@run_time
def Tbl_GP_KSIDPool(lcdb,tradedate):
    tradedate = tradedate.replace("-","")[:8]
    if tradedate>ToDaydate('%Y%m%d'):
        Tbls=lcdb.GetTbls("gp_daysksid")
        Tbls=sorted(list(set([Tbl.split("_")[1] for Tbl in Tbls if "1440" in Tbl])))
        tradedate=Tbls[-1]
    strsql   = f"SELECT trade_date,trade_time,code,kid  FROM gp_daysksid.tbl_{tradedate}_1440 where kid>=60"
    rst  = lcdb.GetData(strsql,True)
    return rst
@run_time
def Tbl_GP_CodeInfo(lcdb):
    strsql   = f"SELECT code,name, 所属同花顺行业 FROM gp_baseinfo.tbl_contract_info "
    rst  = lcdb.GetData(strsql,True)
    return rst
@run_time
def Tbl_GP_BKHQLists(lcdb):
    rst =lcdb.GetTbls("gp_linesbases")
    rst=[x.replace("tbl_","").replace("_",".") for x in rst ]
    return sorted(SetList(rst))
#%% 其他

def Tbl_GP_BKHQLinesHolds(lcdb,tblname,trade_date):
    strsql   = f"SELECT holds FROM gp_linesbases.{tblname} where trade_date ='{trade_date}'"
    rst  = lcdb.GetData(strsql,True)
    codes= (rst["holds"].item()).replace(" ","").split(",")
    if len(codes)>0:
        wherecode=sqlstrselectcode(codes)
        strsql   = f"SELECT trade_date,trade_time,code,period FROM gp_dayshqdb.tbl_{trade_date.replace('-','')}_1440 {wherecode} "
        rst  = lcdb.GetData(strsql,True)
    return rst
def sqlstrselectcode(codes):
    result = ""
    if len(codes) > 0:
        for i, code in enumerate(codes):
            result += f"code='{code}'"  # 使用字符串拼接的方式将每个元素格式化为code='元素值'的形式
            if i < len(codes) - 1:  # 在每个元素之后添加 or
                result += " or "
        if len(result) > 0:
            result = " where " + result
    return result  
#%% Influx查询



#%% 终结





























































