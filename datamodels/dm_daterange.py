'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 19:50:01
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 19:51:19
FilePath: /miaosuan2/datamodels/dm_daterange.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, field_validator, ValidationError

class DateRangeModel(BaseModel):
    start: Optional[date] = None
    end: Optional[date] = None

    @field_validator("start", mode="before")
    @classmethod
    def validate_end(cls, v):
        if v is None:
            return datetime.strptime("1990-01-01" , "%Y-%m-%d").date()
        if isinstance(v, date):
            return v
        try:
            # 强制解析固定格式"%Y-%m-%d"
            return datetime.strptime(v, "%Y-%m-%d").date()
        except Exception:
            raise ValidationError("date must be in YYYY-MM-DD format")
        
    @field_validator("end", mode="before")
    @classmethod
    def validate_start(cls, v):
        if v is None:
            return datetime.strptime("2200-01-01" , "%Y-%m-%d").date()
        if isinstance(v, date):
            return v
        try:
            # 强制解析固定格式"%Y-%m-%d"
            return datetime.strptime(v, "%Y-%m-%d").date()
        except Exception:
            raise ValidationError("date must be in YYYY-MM-DD format")
        