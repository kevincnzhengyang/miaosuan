'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-07 12:14:12
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-17 11:39:33
FilePath: /miaosuan2/pages/api_client.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import json
from datetime import datetime

from config.settings import settings
from localdb.db_qianshou import get_equities
from datamodels.dm_daterange import DateRangeModel
from helper.account_futu import load_equity_finance



def get_stock_list() -> list:
    """获取股票列表"""
    stocks = []
    for e in  get_equities():
        s = dict(e)
        notes = s['note']
        if not notes:
            stocks.append(s)
            continue
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
    return [s['symbol'] for s in get_stock_list()]

def get_financial_report(symbol: str, range: DateRangeModel) -> dict:
    return load_equity_finance(symbol=symbol,
                               start_date=range.start,  # type: ignore
                               end_date=range.end)      # type: ignore

def get_tasks(symbol: str) -> list:
    with open(settings.TASK_FILE, 'r', encoding='utf-8') as file:
        return [task for task in json.load(file) if \
                symbol in task['instrument'].replace(" ", "").split(",")]
