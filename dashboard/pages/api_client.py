'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-07 12:14:12
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-11 22:02:24
FilePath: /miaosuan/dashboard/pages/api_client.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os, json, requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, field_validator, ValidationError
from loguru import logger


# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".." / ".env")
QIANSHOU_URL = os.getenv("QIANSHOU_URL", "http://127.0.0.1:23000")
TASK_FILE = os.getenv("TASK_FILE", "tasks.json")  # 任务定义文件
TASK_FILE = os.path.join(BASE_DIR, "..", TASK_FILE)

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
        
def get_stock_list() -> list:
    """获取股票列表"""
    resp = requests.get(f"{QIANSHOU_URL}/equities")
    # 假设返回列表 [{'symbol': 'AAPL', 'market': 'US', 'note': ''}, ...]
    stocks = []
    for s in  resp.json():
        # note 中是 [{"item": "comunic", "value": 200079356.0}, ...]
        notes = s['note']
        s['note'] = []
        for note in json.loads(notes):
            if note['value'] is None:
                continue
            elif isinstance(note['value'], (int, float)):
                if note['item'] == 'incdate' or note['item'] == 'lsdateipo':
                    datestr = datetime.fromtimestamp(note['value']/1000).date().strftime("%Y-%m-%d")
                    s['note'].append({'item': note['item'],
                                      'value': datestr})
                continue
            # 其它都保留
            s['note'].append(note)
        stocks.append(s)
    return stocks
        
def get_stocks_code() -> list:
    """获取股票列表"""
    resp = requests.get(f"{QIANSHOU_URL}/equities")
    if resp.status_code != 200:
        return []
    # 假设返回列表 [{'symbol': 'AAPL', 'market': 'US', 'note': ''}, ...]
    return [s['symbol'] for s in resp.json()]

def get_financial_report(symbol: str, range: DateRangeModel) -> dict:
    """获取财报数据"""
    resp = requests.post(f"{QIANSHOU_URL}/equity/finance", 
                         params={"symbol": symbol},
                         json=range.model_dump(mode="json"))
    if resp.status_code != 200:
        return dict()
    else:
        return resp.json()  # 假设返回字典形式

def get_tasks(symbol: str) -> list:
    with open(TASK_FILE, 'r', encoding='utf-8') as file:
        return [task for task in json.load(file) if task['instrument'] == symbol]
