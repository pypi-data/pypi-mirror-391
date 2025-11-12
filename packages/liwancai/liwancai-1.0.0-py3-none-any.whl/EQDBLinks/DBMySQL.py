# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 17:32:43 2019
Created on Python3.6.8
@author:
    liwancai
    QQ:248411282
"""
import pymysql
import pandas                       as pd
from liwancai.Functions.LOG        import log
from liwancai.Functions.DirsFile   import ReadToml
from sshtunnel                      import SSHTunnelForwarder
from liwancai.Functions.Formulae   import GETKEY,EVALI,DifEntSet,LinkSelect
#%% SQL数据库
def InitSqlDB(config,KeyName=""):
    if KeyName == "" : KeyName = config["MySqlDB_KeyName"]
    SQLconfig = ReadToml(config["MySqlDB_FileName"],config["MySqlDB_TomlPath"])[KeyName]
    return  MySqlDB(SQLconfig) 


class MySqlDB:
    def __init__(self,config):
        '''
        config={'host':'127.0.0.1','user':'root','password':'password',
                'dbname':"",'tblname':None,'charset':'utf8',"BySSH":False,
                "sshhost":"192.168.31.111","sshport":22,
                "sshuser":"administrator","sshpassword":"123123123"}
        '''
        self.Port = 3306#默认端口
        self.__dict__.update(config)
        self.Connect()
    def RemoteSSH(self):
        '''创建SSH链接服务'''
        self.server = SSHTunnelForwarder(
            ssh_address_or_host=(self.SSHHost, self.SSHPort),  # 指定ssh登录的跳转机的address
            ssh_username=self.SSHUser,  # 跳转机的用户
            ssh_password=self.SSHPassword,  # 跳转机的密码
            remote_bind_address=(self.Host, 3306))
        self.server.start()
    def Connect(self,**arge):
        '''连接数据库'''
        if self.BySSH:
            self.RemoteSSH()
            self.db  = pymysql.connect(host="127.0.0.1",user=self.User,password=self.Password,
                                      db=self.DBName,port=self.server.local_bind_port,
                                      charset=self.Charset,**arge)
        else:self.db = pymysql.connect(host=self.Host,port=self.Port,user=self.User,
                                       password=self.Password,db=self.DBName,
                                       charset=self.Charset,**arge)
        self.cursor = self.db.cursor()#源数据库游标
        self.db.ping(reconnect=True)
    def RunSql(self,string):
        '''
        上报命令
        log.Info(string)
        '''
        try:
            if len(string)<1:return "Sql语句为空"
            self.db.ping(reconnect=True)
            self.ListSQL(string)
            return True
        except Exception as exception:
            log.Error(str(exception))
            errsql = f"SqlErr From:\n{string[:30]}...{string[-30:]}" if len(string)>60 else string
            log.Info(errsql)
            return {"SQL错误":str(exception)}
    def RenameTbl(self,oldtbl,newtbl,temp=False):
        '''
        表格重命名
        temp 临时表不能直接RENAME TABLE
        '''
        if temp: return f"ALTER TABLE {oldtbl} RENAME TO  {newtbl} ;"
        else   : return f"RENAME TABLE {oldtbl} TO {newtbl};"

    def ListSQL(self,strs):
        '''执行SQL语句'''

        if isinstance(strs,list) :
            return [self.RunSql(string) for string in strs ]
        else:return self.cursor.execute(strs)
    def Commit(self):
        '''提交命令'''
        try:
            return self.db.commit()
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def Fetchall(self):
        '''
        获取结果
        这有一个BUG 若重复多次获取则会返回空
        '''
        try:
            return self.cursor.fetchall()
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def Fetchone(self):
        '''获取结果'''
        try:
            return self.cursor.fetchone()
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def Close(self):
        '''关闭'''
        self.db.close()
    def GetTbls(self,usedbname=None):
        '''获取所有的表'''
        try:
            if usedbname!=None:self.UseDB(usedbname)
            self.RunSql("show tables;")
            data=self.Fetchall()
            return sorted([item[0] for item in data ])
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def GetDBs(self):
        '''获取所有的数据库'''
        try:
            self.RunSql("show databases;")
            data=self.Fetchall()
            return  [item[0] for item in data ]
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def CreateDB(self,name,character="utf8"):
        '''创建数据库'''
        sqlmsg = f"create database  IF NOT EXISTS {name} character set {character};"
        print(sqlmsg)
        return self.RunSql(sqlmsg)
    def DropDB(self,name):
        '''删除数据库'''
        return self.RunSql(f"DROP DATABASE IF EXISTS  {name};")
    def UseDB(self,usedbname):
        '''使用数据库'''
        try:
            rst=self.RunSql(f"use {usedbname};")
            self.DBName=usedbname
            return rst
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def CreateTbl(self,tblname,DDL={},Mkey=[],usedbname=None,markupdate=True):
        '''
        创建表
        DDL={}表结构
        Mkey=[]主键key
        INT
        CHAR(8) NOT NULL   定长字符串
        varchar(12) NOT NULL 变长字符串
        decimal(18,3) DEFAULT '0.000' 精准小数
        float(64,6) DEFAULT 0 7位有效数
        Double  DEFAULT NULL  15位有效数
        DATE YYYY-MM-DD	日期
        TIME	HH:MM:SS	时间
        YEAR	YYYY	年份
        DATETIME	YYYY-MM-DD HH:MM:SS	日期和时间
        TIMESTAMP	10位或13位整数（秒数）	时间戳
        "update_time":" datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"

        '''
        if usedbname!=None: tblname=f"{usedbname}.{tblname}"
        if markupdate:DDL["update_time"]="datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        ###--------------------------------------------------------------------
        DDLkey=GETKEY(DDL)
        strddl=""
        # strddl,strkey="",""
        for i in range(len(DDLkey)):
            addstr="" if i<1 else ","
            strddl+=f"{addstr}`{DDLkey[i]}` {DDL[DDLkey[i]]} "
        PMKEY=f",PRIMARY KEY ({self.Tostr(Mkey)})" if len(Mkey)>0 else ""
        DDLstr=f"{strddl}{PMKEY}"
        ###--------------------------------------------------------------------
        sqlstr =f"create table IF NOT EXISTS {tblname}({DDLstr});"
        return self.RunSql(sqlstr)
    def SetIndex(self,tblname,indexname,columns):
        columns_str = ', '.join(columns)# 将字段列表转换为逗号分隔的字符串
        # 生成设置索引的SQL语句
        sql = f"CREATE INDEX {indexname} ON {tblname} ({columns_str});"
        return sql

    def DropTbl(self,tblname,usedbname=None):
        '''删除表'''
        try:
            if usedbname!=None: tblname=f"{usedbname}.{tblname}"
            return self.RunSql(f"DROP TABLE IF EXISTS {tblname};")
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def AddField(self,tblname="test123",Fieldname="test",charset="CHAR(8) NOT NULL",usedbname=None):
        '''增加字段'''
        try:
            if usedbname!=None: tblname=f"{usedbname}.{tblname}"
            return self.RunSql(f"alter table {tblname} add {Fieldname} {charset} ;")
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def DropField(self,tblname="test123",Fieldname="",usedbname=None):
        '''删除字段'''
        try:
            if usedbname!=None: tblname=f"{usedbname}.{tblname}"
            return self.RunSql(f"alter table {tblname} drop {Fieldname};")
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def ModifyField(self,tblname="test123",Fieldname="",usedbname=None,charset="CHAR(8) NOT NULL"):
        '''修改字段属性'''
        try:
            if usedbname!=None: tblname=f"{usedbname}.{tblname}"
            return self.RunSql(f"alter table {tblname} modify {Fieldname} {charset};")
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def ChangeField(self,tblname="test123",nameold="",namenew="",types="varchar(12)",usedbname=None):
        '''修改字段'''
        try:
            if usedbname!=None: tblname=f"{usedbname}.{tblname}"
            return self.RunSql(f"alter table  {tblname} change  {nameold} {namenew} {types};")
        except Exception as exception:
            log.Error(str(exception))
            return str(exception)
    def ReplaceStr(self,tblname="test123",jsdata=[{}],dbname=""):
        '''
        #insert into
        '''
        kss,vss=[],[]
        for js in jsdata:
            k,v=GETKEY(js),list(js.values())
            ks,vs=self.Tostr(k),self.Tostr(v,False)
            kss.append(ks),vss.append(vs)
        columns,value=kss[0],""
        for i in range(len(vss)):
            s="," if i>0 else ""
            value+=f"{s}({vss[i]})"
        if dbname!="" :dbname = f"{self.addtab(dbname)}."
        return f"replace into {dbname}{self.addtab(tblname)} ({columns})values{value};"

    def UpdateStr(self,jsdt,tblname,Mkey,dbname=""):
        if dbname!="" :dbname = f"{self.addtab(dbname)}."
        Value = self.ValueLink(jsdt,keylist=DifEntSet(GETKEY(jsdt),Mkey),CD='SET ',link=",")
        Where = self.ValueLink(jsdt,keylist=Mkey,CD='Where ',link="and")
        return  f"UPDATE {dbname}{self.addtab(tblname)} {Value} {Where} ;"

    def addtab(self,strs,nd=True,NaN=False):
        spt='' if NaN else ("`" if  nd else '"')#子元素什么都不加
        return f"{spt}{strs}{spt}"
    def ValueLink(self,jsdt,keylist=[],CD='Where ',link="and"):
        CDs = [f"{self.addtab(mkey)} ={self.addtab(jsdt[mkey],nd=False)}" for mkey  in keylist]
        return  LinkSelect(CDs,CD,link,False)#条件拼接
    def Update(self,tblname="test123",jsdata=[{}],Mkey=[],dbname=""):
        strs = [self.UpdateStr(jsdt,tblname,Mkey,dbname=dbname) for jsdt in jsdata]
        return strs if len(strs)>1 else strs[0]
    def Updates(self,tblname,jsdata,filed,CDfiled,dbname=""):
        '''
        快速批量update数据
        filed   需要更新值的字段
        CDfiled 独一无二的条件字段

        '''
        CDCases = [f"WHEN  '{jsdt[CDfiled]}' THEN  '{jsdt[filed]}' " for jsdt in jsdata]
        CDCaseS = LinkSelect(CDCases,'',' ',False)
        CDs = [f"'{jsdt[CDfiled]}'" for jsdt in jsdata]
        CDS = LinkSelect(CDs,'',',',True)
        if dbname!="" :dbname = f"{self.addtab(dbname)}."
        string =f"UPDATE {dbname}{tblname} SET {filed} = CASE {CDfiled} {CDCaseS} END WHERE {CDfiled} IN  {CDS};"
        return string
    def Tostr(self,strs,nd=True,NaN=False):
        '''
        nd=True==>>  `A`,`B`,`C`
        nd=False==>>  'A','B','C'
        NaN 子元素 是否添加符号
        '''
        if type(strs)==str or (not hasattr(strs, '__iter__')):return strs
        sx=""
        for i in range(len(strs)):
            s="," if i>0 else ""
            spt='' if NaN else ("`" if  nd else "\'")#子元素什么都不加
            sx+=f"{s}{spt}{self.Tostr(strs[i],nd=False,NaN=True)}{spt}"
        return sx

    def GetData(self,string,rstdf=True,Multiple=True):
        '''
        获取数据
        返回dataframe形式：rstdf=True
        返回columns和values :rstdf=False
        Multiple ==>>Fetchone 或者 Fetchall
        '''
        try:
            self.RunSql(string)
            data=self.Fetchall() #if Multiple else self.Fetchone()
            self.Commit()###主动结束事务避免连续相同查询返回空值
            columns=[field[0] for field in self.cursor.description]#
            # if not  Multiple:return {columns[i]:data[i]  for i in range(len(columns))}
            if rstdf:return pd.DataFrame(data,columns=columns)#返回df类型数据
            else :return {"columns":columns,"data":data}#返回json数据
        except Exception as exception:
            log.Error(str(exception))
            if rstdf :return pd.DataFrame()
            else  :{"columns":None,"data":None}
    def SaveDF(self,df,tblname="test123",method="replace into",Mkey=[],dbname=""):
        '''
        保存df
        replace into 或者 insert into
        update 需要填写Mkey
        '''
        if len(df)<1:return ""
        jsdata = EVALI(df.to_json(orient="records",force_ascii=False))
        return self.SaveJS(jsdata,tblname,method,Mkey,dbname=dbname)
    def SaveJS(self,jsdata:list=[{}],tblname="test123",method="replace into",Mkey=[],dbname=""):
        '''
        jsdata  [{}]
        '''
        if len(jsdata)<1:return ""
        if method=="update":       string = self.Update(tblname,jsdata,Mkey)
        if method=="replace into": string = self.ReplaceStr(tblname,jsdata,dbname=dbname)
        return string

def SaveJSToLCDB(lcdb,jsdatas,tblname,dbname):
    '''保存到MySql'''
    try:
        lcdb.UseDB(dbname)
        savesqls=lcdb.SaveJS(jsdatas,tblname)
        lcdb.RunSql(savesqls)
        lcdb.Commit()
        return True
    except Exception as exception:log.Error(str(exception))

