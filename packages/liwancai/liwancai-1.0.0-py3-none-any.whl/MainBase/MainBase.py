# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 20:07:00 2019
Created on Python3.6.8
@author:liwancai
    QQ:248411282
    Tel:13199701121
"""
import os,inspect,time,socket
from liwancai.Functions.LOG            import log
from liwancai.Functions.DirsFile       import ReadToml
from liwancai.EQUseApi.ApiBase         import SetUseapi
from liwancai.EQUseApi.ApiFunc         import Api_EQsRobotSend
from liwancai.Functions.Formulae       import GETKEY,NowDatetime
class SetMainBase():
    def __init__(self,AppName, DataPath,config):
        self.config     = config
        self.AppName    = AppName
        self.DataPath   = DataPath
        self.InitTSEQApi()
        self.GetLocalIP()
        self.Start()
        self.update_runtime()
        
    def update_runtime(self):
        self.e_time = time.time()
        self.runtime = round(self.e_time - self.s_time, 3)
        if self.runtime < 60:
            self.RunTime = f"{self.runtime} 秒"
        elif self.runtime < 3600:
            self.RunTime = f"{round(self.runtime / 60, 1)} 分钟"
        elif self.runtime < 86400:
            self.RunTime = f"{round(self.runtime / 3600, 1)} 小时"
        else:
            self.RunTime = f"{round(self.runtime / 86400, 1)} 天"
    def InitTSEQApi(self):
        self.EQUseApi = SetUseapi(self.config )
    def Start(self):
        self.s_time = time.time()
        strmsg=f"■|服务器【{self.ip}】启动\n■|程序: {self.AppName}.py\n■|时间: {NowDatetime()}"
        Api_EQsRobotSend(self.EQUseApi ,strmsg,self.config["SendToGroupList"],"msg")
        log.Info(strmsg)
    def Stop(self):
        self.update_runtime()
        strmsg=f"■|服务器【{self.ip}】完成\n■|程序: {self.AppName}.py\n■|耗时: {self.RunTime}"
        Api_EQsRobotSend(self.EQUseApi ,strmsg,self.config["SendToGroupList"],"msg")
        log.Info(strmsg)
    def GetLocalIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip  = s.getsockname()[0]
        s.close()
def GetConfig():
    caller_frame = inspect.currentframe().f_back
    caller_filename = caller_frame.f_code.co_filename
    AppName = os.path.basename(caller_filename).replace(".py", "").replace(".PY", "")
    DataPath = f"./Apps/{AppName}/Datas/"
    config = ReadToml("config", path=f"{DataPath}/etc/")
    for key in GETKEY(config):
        if type(config[key])==str:
            if config[key].find("./Datas/") > -1:
                config[key] = config[key].replace("./Datas/", DataPath)
    return AppName, DataPath,config