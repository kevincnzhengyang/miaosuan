'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 19:55:37
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 19:56:12
FilePath: /miaosuan2/localdb/dm_quote.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
from pydantic import BaseModel

class QuoteOHLC(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    pct_chg: float  # 百分比涨跌
    pct_amp: float  # 百分比振幅
    volume: int
    