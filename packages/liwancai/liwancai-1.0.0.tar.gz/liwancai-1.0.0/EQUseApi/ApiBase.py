# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 20:07:00 2019
Created on Python3.6.8
@author:liwancai
    QQ:248411282
    Tel:13199701121
"""
import os,inspect,time
import requests,json,socket
from liwancai.Functions.LOG           import log
from liwancai.Functions.DirsFile      import ReadToml
def SetUseapi(config):
    EQUseApi_CFG = ReadToml(config["EQUseApi_FileName"],config["EQUseApi_TomlPath"])
    return EQUseApi(EQUseApi_CFG)
###############################################################################
class EQUseApi:
    def __init__(self,config):
        self.ip         = ""
        self.cookies    = None
        self.session    = requests.Session()
        self.BaseUrl    = config["EQDataHTTPAPI"]
        self.Token      = config["EQDataApiToken"]
        self.SendList   = config["SendToGroupList"]
        self.headers    = {'content-type': 'application/json;charset=utf-8',
                          "Authorization":self.Token,'Connection':'keep-alive'}#
        self.session.headers.update(self.headers)
        self.SetIP()
    def SetIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip  = s.getsockname()[0]
        s.close()
    def SetApiToken(self,EQDataApiToken):
        self.Token=EQDataApiToken
        self.headers["Authorization"]=self.SetApiToken
        self.session.headers.update(self.headers)
    def Login(self,ApiEndUrl,username,password):
        loginbody = { "TELorEmail": username, "Password": password }
        response = self.Request(loginbody,ApiEndUrl)
        if response.status_code == 200:
            self.cookies = response.cookies
            self.session.cookies.update(self.cookies)
        return response.json()
    def Request(self,body,ApiEndUrl,HTTPS =False):
        try:
            for i in range(len(self.BaseUrl)):
                baseurl   = (f"{self.BaseUrl[i]}/{ApiEndUrl}").replace("//","/")
                urlheader = "https://" if HTTPS else "http://"
                url       = urlheader + baseurl # 完整接口网址
                response  = self.session.post(url, data=json.dumps(body))#
                if response.status_code != 200 and (i<(len(self.BaseUrl)-1)):
                    log.Warn(f"||{url}请求失败,重新请求第{i+1}次||")
                    continue
                else: return response
        except Exception as exception: log.Error(exception)  
    def PostData(self,body,ApiEndUrl):
        response = self.Request(body,ApiEndUrl)
        return  response.json()  if response!=None else {}
        
###///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
 