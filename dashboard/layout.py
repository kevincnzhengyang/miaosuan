'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-10 21:25:09
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-11 12:07:02
FilePath: /miaosuan/dashboard/layout.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

from dash import html, dash
import dash_bootstrap_components as dbc
import dash

from dashboard import app

# 顶部导航栏
navbar = dbc.NavbarSimple(
    brand="量化金融平台",
    brand_href="/",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("关注股票", href="/")),
        dbc.NavItem(dbc.NavLink("财务报表", href="/financials")),
        dbc.NavItem(dbc.NavLink("量化分析", href="/analysis")),
    ]
)

# Dash 应用 layout
app.layout = dbc.Container(
    [
        navbar,
        dash.page_container  # 动态加载多页面内容
    ],
    fluid=True
)
