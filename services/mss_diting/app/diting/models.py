'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 13:06:10
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-23 13:23:42
FilePath: /mss_diting/app/diting/models.py
Description: 数据模型

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

from pydantic import BaseModel

class Rule(BaseModel):
    symbol: str
    condition: str
    threshold: float
    webhook_url: str
    cooldown_sec: int = 60
    note: str = ""
    enabled: bool = True

class Trigger(BaseModel):
    id: int | None = None
    rule_id: int
    symbol: str
    message: str
