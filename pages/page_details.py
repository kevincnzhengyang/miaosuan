'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-11 22:16:40
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-11 22:17:06
FilePath: /miaosuan/dashboard/pages/page_details.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import dash
from dash import html, dcc, callback, Input, Output
from urllib.parse import parse_qs

dash.register_page(__name__, path="/details", name="任务详情")

layout = html.Div([
    html.H3("任务详情"),
    dcc.Location(id="url", refresh=False),
    html.Div(id="details-content")
])

@callback(
    Output("details-content", "children"),
    Input("url", "search")
)
def show_details(query_string):
    if not query_string:
        return "未提供股票代码"
    params = parse_qs(query_string.lstrip("?"))
    code = params.get("code", [""])[0]
    return html.Div([
        html.P(f"股票代码: {code}"),
        html.P("这里可以展示该股票的量化分析结果……")
    ])
