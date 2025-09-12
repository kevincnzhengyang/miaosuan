'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-27 21:12:28
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 19:49:15
FilePath: /miaosuan2/datamodels/dm_indicator.py
Description: 数据模型

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

from typing import List
from pydantic import BaseModel, Field

class IndicatorDef(BaseModel):
    name: str = Field(..., pattern=r"^[A-Z0-9_]+$")  # type: ignore
    description: str = ""
    formula: str

class IndicatorSet(BaseModel):
    set_name: str
    description: str = ""
    indicators: List[IndicatorDef]
    