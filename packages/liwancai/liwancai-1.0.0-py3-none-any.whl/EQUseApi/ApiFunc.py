
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 20:07:00 2019
Created on Python3.6.8
@author:liwancai
    QQ:248411282
    Tel:13199701121
"""
import json,requests,time
from liwancai.Functions.LOG import log
from liwancai.Functions.Formulae      import DfToType,ToDaydate
###///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def Api_EQsRobotSend(EQUseApi,
 content:str ="", towxid =[], msgtype ="text", 
 atlist=[]):
    if  "■|服务器" not in content:
        content += f"\n【{EQUseApi.ip}】->【{time.strftime('%H:%M:%S', time.localtime())}】"
    if len(towxid)<1: towxid =EQUseApi.SendList
    webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="
    try:
        # 根据消息类型构造请求体
        if msgtype == "text" or msgtype == "msg":
            body = {
                "msgtype": "text",
                "text": {
                    "content": content,
                    "mentioned_list": atlist if atlist else [],
                    "mentioned_mobile_list": []
                }
            }
        elif msgtype in ["markdown", "markdown_v2"]:
            body = {
                "msgtype": msgtype,
                msgtype: {
                    "content": content
                }
            }
        else:
            # 默认使用text类型
            body = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
        
        # 发送请求到企业微信webhook
        headers = {'Content-Type': 'application/json'}
        responses = []
        for wxid in towxid:
            response = requests.post(webhook_url+wxid, headers=headers, data=json.dumps(body))
            responses.append(response.json())
        return  responses
    except Exception as e:
        log.Error(f"企业微信消息发送失败: {str(e)}")
        return False
###///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def Api_EQsTradeDates(EQUseApi,year=int(ToDaydate()[:4])):
    data = EQUseApi.PostData({"year": year},"/EQsApi/EQsTradeDates")
    return data 
###///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

###///////////////////////////////////////////////////////////////////////////////////////////////////////////////////