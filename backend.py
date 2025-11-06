'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-27 20:55:11
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-11-06 12:04:51
FilePath: /miaosuan/backend.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import os
from pathlib import Path

from loguru import logger
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.settings import settings
from services.mss_diting.quote_manager import manager
from services.mss_diting.quote_futu import FutuEngine
from services.mss_qianji.qtr_abnormal import update_rule_of_equities
from services import chuanyin, diting, qianshou


BASE_DIR = Path(__file__).resolve().parent

# 记录日志到文件
logger.add(os.path.join(BASE_DIR, settings.LOG_DIR, "miaosuan.log"), 
            level=settings.LOG_LEVEL, 
            rotation="50 MB", retention=5)

# 定时任务
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("妙算服务启动...")
    # 注册多个行情引擎
    manager.register(FutuEngine())

    # 启动所有引擎
    manager.start_all()
    scheduler.add_job(update_rule_of_equities, "cron", 
                    day_of_week="0-6",
                    hour=7, 
                    minute=0,
                    id="rule_daily")
    scheduler.add_job(manager.daily_all, "cron", 
                    day_of_week="0-6", 
                    hour=settings.CRON_HOUR, 
                    minute=settings.CRON_MINUTE,
                    id="engines_daily")
    scheduler.start()
    yield
    scheduler.shutdown()
    # 关闭所有
    manager.stop_all()
    logger.info("妙算服务关闭...")

fastapi = FastAPI(lifespan=lifespan, title="MiaoSuan Service")

fastapi.include_router(chuanyin.router)
fastapi.include_router(diting.router)
fastapi.include_router(qianshou.router)
