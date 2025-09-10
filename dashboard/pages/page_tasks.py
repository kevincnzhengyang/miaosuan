'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-10 19:44:34
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-10 20:02:26
FilePath: /miaosuan/dashboard/pages/page_tasks.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/tasks", name="量化分析")

layout = dbc.Container([
    html.H2("量化分析页面"),
    html.P("这里将展示回测结果、技术指标和量化策略分析。")
], fluid=True)