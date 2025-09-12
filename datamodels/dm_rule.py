'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 19:54:47
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 19:56:04
FilePath: /miaosuan2/datamodels/dm_rule.py
Description: 

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
