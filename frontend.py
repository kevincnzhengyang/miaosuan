'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-10 18:01:27
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 20:19:06
FilePath: /miaosuan2/dashboard/frontend.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os, dash
from loguru import logger
from pathlib import Path
import dash_bootstrap_components as dbc

from config.settings import settings

BASE_DIR = Path(__file__).resolve().parent

# 记录日志到文件
logger.add(os.path.join(BASE_DIR, settings.LOG_DIR, "dashboard.log"), 
            level=settings.LOG_LEVEL, 
            rotation="50 MB", retention=5)

# 使用Bootstrap主题
dashapp = dash.Dash(__name__, 
                use_pages=True, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

dashapp.title = "个人量化金融平台"

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

dashapp.layout = dbc.Container(
    [
        navbar,
        dash.page_container
    ],
    fluid=True
)
