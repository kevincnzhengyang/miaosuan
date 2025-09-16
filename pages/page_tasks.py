'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-10 19:44:34
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-11 22:26:39
FilePath: /miaosuan/dashboard/pages/page_tasks.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, dash_table
from typing import Any, Dict, List, cast

from .api_client import get_stocks_code, get_tasks


dash.register_page(__name__, path="/tasks", name="量化分析")


layout = dbc.Container([
    html.H3("量化分析任务列表"),

    # 用于缓存股票列表
    dcc.Store(id="stock-options-store2"),

    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id="stock-code-dropdown2", 
            placeholder="请选择或输入股票代码", 
            searchable=True,
            clearable=True
        ), width=3),

        dbc.Col(dbc.Button("查询", id="query-button", color="primary"), width="auto", className="me-2"),
        # dbc.Col(dbc.Button("分析", id="quant-button", color="success"), width="auto")

        dbc.Col(
            html.A(
                dbc.Button("分析", id="analyze-btn", color="success", outline=True),
                id="analyze-link",
                href="",
                target="_blank"  # 新开页面
            ),
            width="auto"
        ),
    ], className="mb-3"),

    html.Div(id="tasks-output")
    
], fluid=True)

def create_table(data: list, title: str):
    """工具函数：将财务数据渲染为 DataTable"""
    if not data:
        return html.P(f"{title} 暂无数据")

    # 自动生成表头
    columns = cast(List[Dict[str, Any]], [
        {"name": "任务ID", "id": "task_id"},
        {"name": "模型名称", "id": "model"},
        {"name": "训练开始", "id": "train_start"},
        {"name": "训练结束", "id": "train_end"},
        {"name": "回测开始", "id": "backtest_start"},
        {"name": "回测结束", "id": "backtest_end"},
    ])

    return dbc.Card([
        dbc.CardHeader(html.H5(title)),
        dbc.CardBody(
            dash_table.DataTable(
                columns=columns,  # type: ignore
                data=data,
                page_size=10,
                style_table={"overflowX": "auto"},
                style_cell={
                    "padding": "8px",
                    "fontSize": "14px",
                    "textAlign": "center"
                },
                style_header={
                    "backgroundColor": "#f8f9fa",
                    "fontWeight": "bold"
                }
            )
        )
    ], className="mb-4")

# 🔹 回调 1：加载股票列表，写入 dcc.Store
@dash.callback(
    Output("stock-options-store2", "data"),
    Input("stock-code-dropdown2", "id"),   # 页面加载时触发
)
def load_stock_options(_):
    return get_stocks_code()

# 🔹 回调 2：更新 Dropdown options
@dash.callback(
    Output("stock-code-dropdown2", "options"),
    Input("stock-options-store2", "data")
)
def update_dropdown_options(options):
    return options or []

# 回调函数
@dash.callback(
    Output("tasks-output", "children"),
    Input("query-button", "n_clicks"),
    State("stock-code-dropdown2", "value"),
    prevent_initial_call=True
)
def query_tasks_data(n_clicks, code):
    if not code:
        return html.P("请输入股票代码")

    try:
        data = get_tasks(symbol=code)
        return [
            create_table(data, "量化分析任务列表"),
        ]

    except Exception as e:
        return html.P(f"请求出错: {e}")

# 2️⃣ 分析按钮：生成跳转链接
@dash.callback(
    Output("analyze-link", "href"),
    Input("analyze-btn", "n_clicks"),
    State("stock-code-dropdown2", "value"),
    prevent_initial_call=True
)
def open_analysis(n_clicks, code):
    if not code:
        return "/details"
    return f"/details?code={code}"
