# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 17:32:43 2019
Created on Python3.6.8
@author:
    liwancai
    QQ:248411282
"""
import requests
import pandas                           as pd
from liwancai.Functions.LOG        import log
class THS_HotBKsRank:
    def __init__(self):
        pass
    def get_headers(self):

        headers={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        }
        return headers

    def getData(self):
        url='https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/plate?'
        params={
            'type': 'concept'
        }
        headers=self.get_headers()
        res=requests.get(url=url,params=params,headers=headers)
        text=res.json()
        status_code=text['status_code']
        if int(status_code)==0:
            df=pd.DataFrame(text['data']['plate_list'])
            df=df.rename(columns={"code":"概念代码","name":"概念名称"})
            return df
        else:
            log.Error(f"同花顺板块热度数据获取失败")
            return pd.DataFrame()