'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 18:04:49
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 18:26:54
FilePath: /miaosuan/dashboard/core/qtr_abnromal.py
Description: 市场异常交易监控规则

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os, sys, qlib
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv


# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".." / ".env")
DATA_DIR = os.path.expanduser(os.getenv("DATA_DIR", "~/Quanter/qlib_data"))
DITING_URL = os.path.join("DITING_URL", "http://192.168.3.3:21000")
CHUANYIN_URL = os.path.join("CHUANYIN_URL", "http://192.168.3.3:22000") 
DITING_DIR = os.path.join(BASE_DIR / ".." / ".." / "services" / "mss_diting" / "app")
sys.path.append(DITING_DIR)
from diting.models import Rule  # type: ignore warnings


