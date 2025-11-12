# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 17:32:43 2019
Created on Python3.6.8
@author:
    liwancai
    QQ:248411282
""" 
from liwancai.Functions.LOG           import log
from liwancai.Functions.DirsFile      import ReadToml

def GetTomlDDLMkey(FileName: str, FilePath: str="", COMMENT: bool=True):
    if FilePath == "":
        FilePath = "./Datas/MySqlDDLMkeys/"
    log.Info(f"【开始】读取{FilePath}{FileName}的DDL,MKey配置信息")
    DDLMkeyS = ReadToml(FileName, FilePath)
    ddl = {key: str(value) for key, value in DDLMkeyS["DDL"].items()}
    mkey = [str(item) for item in DDLMkeyS["Mkey"]]
    if COMMENT and "COMMENT" in DDLMkeyS:
        comment_dict = {key: str(value) for key, value in DDLMkeyS["COMMENT"].items()}
        for key, value in comment_dict.items():
            ddl[key] = f"{ddl[key]} COMMENT '{value}'"
    log.Info(f"【结束】读取{FilePath}{FileName}的DDL,MKey配置信息")
    return ddl, mkey
