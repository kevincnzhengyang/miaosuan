'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 18:48:50
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 21:16:19
FilePath: /miaosuan2/config/settings.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_DIR: str = "."
    # 日志设置
    LOG_DIR: str = "logs"
    LOG_LEVEL: str = "DEBUG"
    # 数据路径
    DATA_DIR: str = "~/Quanter/qlib_data"
    QLIB_DIR: str = "~/Quanter/qlib"
    RPT_DIR: str = "financials"
    INDS_DIR: str = "indicators"
    RECS_DIR: str = "recs"
    OCSV_DIR: str = 'ocsv'
    CSV_DIR: str = "csv"
    # 本地数据库
    DB_FILE: str = "miaosuan.db"
    # 任务文件
    TASK_FILE: str = "tasks.json"
    # FutuOpenAPI设置
    FUTU_API_HOST: str = "127.0.0.1"
    FUTU_API_PORT: int = 21111
    FUTU_GROUP_NAME: str = "量化分析"
    SYNC_INTERV_M: int = 5
    QUOTE_INTERVAL: int = 5
    COOLING_CYCLE: int = 10
    CRON_HOUR: int = 5
    CRON_MINUTE: int = 30
    # IM参数设置
    TELEGRAM_BOT_TOKEN: str = "7770285470:AAFoHL0VyWYNQVa8iqL9tTbv2FR9AHA4-TQ"
    LINE_ACCESS_TOKEN: str = "8XICVZ0fteocnsPLJzzh3NYF2JqS5OQ08D+DDtJe25zcfCA3iRQW5ZANyfQVtrpePQlMMjsYWTkWpoxrpRfXA9qvbR7/0Wq+CGn/yFaFldqY9bo8wCW8jtP25w0Au4OGYnMlMtiGrDIS69zhAEfqXgdB04t89/1O/w1cDnyilFU="
    LINE_USER_ID: str = "U334650e4b7488ceb5e446ad1a2bd6c67"
    # 服务参数设置
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 21080
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 21099

    class Config:
        env_file = ".env"            # 自动读取项目根目录 .env
        env_file_encoding = "utf-8"  # 编码

# 创建全局配置对象
settings = Settings()


# 初始化各个子路径和文件
settings.BASE_DIR = str(Path(__file__).resolve().parent / "..")
settings.LOG_DIR = os.path.join(settings.BASE_DIR, settings.LOG_DIR)
settings.INDS_DIR = os.path.join(settings.BASE_DIR, settings.INDS_DIR)
settings.RECS_DIR = os.path.join(settings.BASE_DIR, settings.RECS_DIR)

settings.OCSV_DIR = os.path.join(settings.DATA_DIR, settings.OCSV_DIR)
settings.CSV_DIR = os.path.join(settings.DATA_DIR, settings.CSV_DIR)
settings.RPT_DIR = os.path.join(settings.DATA_DIR, settings.RPT_DIR)

os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.RPT_DIR, exist_ok=True)
os.makedirs(settings.OCSV_DIR, exist_ok=True)
os.makedirs(settings.CSV_DIR, exist_ok=True)

os.makedirs(os.path.join(settings.DATA_DIR, "calendars"), exist_ok=True)
os.makedirs(os.path.join(settings.DATA_DIR, "features"), exist_ok=True)
os.makedirs(os.path.join(settings.DATA_DIR, "instruments"), exist_ok=True)
