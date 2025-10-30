'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 18:48:50
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-10-30 09:18:45
FilePath: /miaosuan/config/settings.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os, pytz, datetime
from pathlib import Path
from pydantic_settings import BaseSettings
from loguru import logger


def _diff_hours() -> int:
    now = datetime.datetime.now().astimezone()

    target_tz = pytz.timezone("Asia/Shanghai")  # 指定时区-北京时间
    target_time = datetime.datetime.now(target_tz)

    offset_current = now.utcoffset()
    offset_target = target_time.utcoffset()
    if (offset_current is None) or (offset_target is None):
        logger.warning("无法获取时区偏移信息")
        return 0
    
    diff_hours = (offset_current - offset_target).total_seconds() / 3600
    logger.info(f"当前时区:{now.tzinfo}, 时差: {diff_hours}")
    return int(diff_hours)

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
    FUTU_GROUP_QUANTER: str = "量化分析"
    FUTU_GROUP_OPTION: str = "期权分析"
    QUOTE_INTERVAL: int = 5
    COOLING_CYCLE: int = 10
    CRON_HOUR: int = 5
    CRON_MINUTE: int = 30
    # IM参数设置
    TELEGRAM_BOT_TOKEN: str = ""
    LINE_ACCESS_TOKEN: str = ""
    LINE_USER_ID: str = ""
    # 服务参数设置
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 21080
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 21099

    class Config:
        env_file = ".env"            # 自动读取项目根目录 .env
        env_file_encoding = "utf-8"  # 编码
        extra = "allow"

# 创建全局配置对象
settings = Settings()


# 初始化各个子路径和文件
settings.BASE_DIR = str(Path(__file__).resolve().parent / "..")
settings.LOG_DIR = os.path.join(settings.BASE_DIR, settings.LOG_DIR)
settings.INDS_DIR = os.path.join(settings.BASE_DIR, settings.INDS_DIR)
settings.RECS_DIR = os.path.join(settings.BASE_DIR, settings.RECS_DIR)


settings.DATA_DIR = os.path.expanduser(settings.DATA_DIR)
settings.QLIB_DIR = os.path.expanduser(settings.QLIB_DIR)
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

# 调整CRON_HOUR以适应当前时区
settings.CRON_HOUR += _diff_hours()
