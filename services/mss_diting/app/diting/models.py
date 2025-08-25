'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 13:06:10
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-25 09:19:49
FilePath: /mss_diting/app/diting/models.py
Description: 数据模型

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

from pydantic import BaseModel

class Rule(BaseModel):
    id: int | None = None
    name: str
    symbol: str
    brokers: str
    rule_json: str
    webhook_url: str
    tag: str
    note: str = ""
    enabled: bool = True
    updated_at: str | None = None

class Trigger(BaseModel):
    id: int | None = None
    rule_id: int
    symbol: str
    message: str
    ts: str | None = None

class QuoteOHLC(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    pct_chg: float  # 百分比涨跌
    pct_amp: float  # 百分比振幅
    volume: int
    