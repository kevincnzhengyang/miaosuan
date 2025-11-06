'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-11-06 12:16:36
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-11-06 12:24:45
FilePath: /miaosuan/services/mss_qianji/ta_daily.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
from loguru import logger

from config.settings import settings
from datamodels.dm_equity import Equity
from localdb.db_qianshou import get_equities
from services.mss_qianji.ta_hly import ta_hly_analysis


async def ta_daily_analysis():
    logger.info("开始每日技术分析")
    for row in get_equities(only_valid=True):
        e = Equity(**dict(row))
        await ta_hly_analysis(symbol = e.to_futu_symbol(), 
                              span=settings.DATA_SPAN,  # type: ignore
                              n_forecast=settings.N_FORECAST) # type: ignore
    logger.info("完成每日技术分析")
