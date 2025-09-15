'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-27 20:55:11
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-15 19:07:02
FilePath: /miaosuan2/services/qianshou.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

from loguru import logger
from fastapi import APIRouter

from localdb.db_qianshou import *
from datamodels.dm_equity import Equity
from datamodels.dm_daterange import DateRangeModel
from localdb.db_qianshou import get_equities
from helper.indicator_tools import load_all_indicators
from helper.hist_futu import futu_update_daily
from helper.bin_tools import load_equity_quote
from helper.account_futu import *
from services.mss_qianji.qtr_abnormal import update_rule_of_equities


router = APIRouter(
    prefix="/diting",
    tags=["DiTing"],
)

@router.get("/equities")
def list_equities_api():
    rows = get_equities(only_valid=False)
    return [Equity(**row) for row in rows]

@router.get("/indicators")
def list_indicators_api():
    return load_all_indicators()

@router.post("/equity/finance")
def get_equity_finance(symbol: str, range: DateRangeModel):
    return load_equity_finance(symbol, range.start, range.end)  # type: ignore

@router.post("/equity/quote")
def get_equity_quote(symbol: str, range: DateRangeModel):
    return load_equity_quote(symbol, range.start, range.end)  # type: ignore

@router.post("/update/futu/daily")
def update_futu_daily_api():
    futu_update_daily()
    return {"status":"ok"}

@router.post("/sync/futu/group")
async def sync_futu_group_api():
    await futu_sync_group()
    return {"status":"ok"}

@router.post("/update/rules")
async def update_all_rule_equities():
    update_rule_of_equities()
    return {"status":"ok"}
