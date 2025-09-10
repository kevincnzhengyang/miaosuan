'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-10 19:44:03
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-10 20:01:44
FilePath: /miaosuan/dashboard/pages/page_financials.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/financials", name="财务报表")

layout = dbc.Container([
    html.H2("财报页面"),
    html.P("这里将展示财报详细数据和图表。")
], fluid=True)
