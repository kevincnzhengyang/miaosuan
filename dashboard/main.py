'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-10 18:01:27
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-11 12:06:39
FilePath: /miaosuan/dashboard/main.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os, dash
from loguru import logger
from dotenv import load_dotenv
from pathlib import Path
from dash import html
import dash_bootstrap_components as dbc

from dashboard import app

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")
LOG_FILE = os.getenv("LOG_FILE", "dashboard.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "21080"))

# 记录日志到文件，日志文件超过500MB自动轮转
logger.add(LOG_FILE, level=LOG_LEVEL, rotation="50 MB", retention=5)

navbar = dbc.NavbarSimple(
    brand="量化金融平台",
    brand_href="/",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("关注股票", href="/")),
        dbc.NavItem(dbc.NavLink("财务报表", href="/financials")),
        dbc.NavItem(dbc.NavLink("量化分析", href="/tasks")),
    ]
)

app.layout = dbc.Container(
    [
        navbar,
        dash.page_container
    ],
    fluid=True
)

if __name__ == "__main__":
    app.run(debug=True, host=APP_HOST, port=APP_PORT)
    
