# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 17:32:43 2019
Created on Python3.6.8
@author:
    liwancai
    QQ:248411282
"""
import redis
from liwancai.Functions.LOG      import log
from liwancai.Functions.Formulae import GETKEY
from liwancai.Functions.DirsFile import ReadToml
#%% Redis数据库
def RdStConfig(keyname=None,filename="RedistDB",path="./Datas/etc/"):
    '''
    读取数据库配置文件
    [cfg_127]
    host='localhost'
    port=6379
    password=""
    db = 0

    '''
    try:
        cfgall=ReadToml(filename,path)
        return cfgall[keyname] if keyname else cfgall
    except Exception as exception:log.Error(str(exception))

def InitRdStDB(config,name,KeyName=""):
    if KeyName == "" : KeyName = config["RedisDB_KeyName"]
    SQLconfig = ReadToml(config["RedisDB_FileName"],config["RedisDB_TomlPath"])[KeyName]
    return  RdSt(name,SQLconfig) 

class RdSt:
    def __init__(self, name="",RDLINKCFG={"host":"localhost","port":6379,"password":248411282,"dbnum":0}):
        self.name = f"{name}_" 
        self.RD   = redis.Redis(host=RDLINKCFG['host'], port=RDLINKCFG['port'], password=RDLINKCFG['password'], db=RDLINKCFG['dbnum'], decode_responses=True)
    def RecodeH(self,name):
        self.HSetNX("所有表名",name,1)
    def GetAllH(self):
        return self.HGetall("所有表名")
    def PubMsg(self,group,strdata):
        '''发布信息'''
        self.RD.publish(f"{self.name}{group}",strdata)
    def SubGroup(self,group:str):
        '''
        订阅发布
        :param group:"MA309
        '''
        sub = self.RD.pubsub()
        sub.subscribe(f"{self.name}{group}")
        return sub
    def SubData(self,sub):
        '''用于循环获取订阅信息'''
        message = sub.listen()
        for msg in message:
            if msg["type"] == 'message': return msg
    def HSet(self, name, key, value):
        '''赋值'''
        self.RecodeH(name)
        self.RD.hset(name=self.name + name, key=key, value=value)
    def HGet(self, name, key=None):
        '''取值'''
        return self.RD.hget(self.name + name, key) if key != None else self.RD.hgetall(self.name + name)
    def HGetall(self, name):
        '''获取全部key和值'''
        return self.RD.hgetall(self.name + name)  #
    def HExist(self, name, key):
        return self.RD.hexists(name=self.name + name, key=key)
    def HKeyS(self, name):
        '''取Key'''
        return self.RD.hkeys(self.name + name)
    def HLen(self, name):
        '''数据长度'''
        return self.RD.hlen(self.name + name)
    def HmSet(self,name,JSON):
        '''字典赋值'''
        self.RecodeH(name)
        data={key:str(JSON[key]) for key in GETKEY(JSON)}
        return self.RD.hmset(self.name+name,mapping=data)
    def HmGet(self, name, KEYS):
        '''取字典keys值'''
        return self.RD.hmget(name=self.name + name, keys=KEYS)
    def HSetNX(self, name, key, value):
        '''如果表或字段不存在就添加数据，如果表或字段存在就不操作'''
        self.RD.hsetnx(name=self.name + name, key=key, value=value)
    def Hvals(self, name):
        '''返回表中所有值'''
        return self.RD.hvals(self.name + name)
    def HintB(self, name, key, amount):
        '''加减整数'''
        self.RD.hincrby(self.name + name, key, amount)
    def HfloatB(self, name, key, amount):
        '''加减浮点数'''
        self.RD.hincrbyfloat(self.name + name, key, amount)
    def HDel(self, name, keys):  #
        '''删除指定表的指定Key'''
        self.RD.hdel(self.name + name, keys)
    def Flushall(self):
        '''清空内存数据'''
        self.RD.flushall()  #
    def Flushdb(self, name):
        '''清空数据库但可恢复'''
        self.RD.flushdb(self.name + name)  #
    def Delete(self,keys):
        for key in keys:
            self.RD.delete(key)
        log.Info(f"删除数据库数据成功")
    def SelectDB(self,dbnum):
        self.RD.select(dbnum)
    def GetDBKeys(self):
        return self.RD.keys()
        
if __name__ == '__main__':
        
        
    RDBS=RdSt("TRUE")
    # 
    RDBS.HmSet("SS",{"A":0,"B":1,"C":2})
    # RDBS.HmSet("BB",{"A":0,"B":1,"C":2})
    dt=RDBS.HmGet("SS",["A","B","C"])
    print(dt)
    RDBS.HDel("SS","A")
    RDBS.HSetNX("SS","A",888)
    dt=RDBS.HmGet("SS",["A","B","C"])
    print(dt)
    RDBS.HmSet("BB",{"A0":20,"B0":12,"C0":22})
    RDBS.Flushdb("SS")
    dt=RDBS.HmGet("SS",["A","B0","C"])
    dtB=RDBS.HmGet("BB",["A0","B0","C0"])
    print(dt,dtB)
    RDBS.HintB("SS","B",3)
    RDBS.HfloatB("SS","A",2)
    dt=RDBS.HmGet("SS",["A","B","C"])
    print(dt)
    dt=RDBS.HGetall("BB")
    print(dt)
            
        
        