'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-10 19:44:03
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-11 21:38:40
FilePath: /miaosuan/dashboard/pages/page_financials.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, dash_table
from typing import Any, Dict, List, cast

from .api_client import get_stocks_code, get_financial_report, DateRangeModel


dash.register_page(__name__, path="/financials", name="财务报表")

layout = dbc.Container([
    html.H2("财报页面"),

    # 用于缓存股票列表
    dcc.Store(id="stock-options-store"),

    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id="stock-code-dropdown", 
            placeholder="请选择或输入股票代码", 
            searchable=True,
            clearable=True
        ), width=3),

        dbc.Col(dcc.DatePickerSingle(
            id="start-date",
            display_format="YYYY-MM-DD",
            placeholder="开始日期"
        ), width=2),

        dbc.Col(dcc.DatePickerSingle(
            id="end-date",
            display_format="YYYY-MM-DD",
            placeholder="结束日期"
        ), width=2),

        dbc.Col(dbc.Button("查询", id="query-button", color="primary"), width="auto")
    ], className="mb-3"),
    
    html.Div(id="financial-output")
], fluid=True)

def create_table(data: list, title: str):
    """工具函数：将财务数据渲染为 DataTable"""
    if not data:
        return html.P(f"{title} 暂无数据")

    # 自动生成表头
    columns = cast(List[Dict[str, Any]], [{"name": col, "id": col} for col in data[0].keys()])

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
    Output("stock-options-store", "data"),
    Input("stock-code-dropdown", "id"),   # 页面加载时触发
)
def load_stock_options(_):
    return get_stocks_code()

# 🔹 回调 2：更新 Dropdown options
@dash.callback(
    Output("stock-code-dropdown", "options"),
    Input("stock-options-store", "data")
)
def update_dropdown_options(options):
    return options or []

# 回调函数
@dash.callback(
    Output("financial-output", "children"),
    Input("query-button", "n_clicks"),
    State("stock-code-dropdown", "value"),
    State("start-date", "date"),
    State("end-date", "date"),
    prevent_initial_call=True
)
def query_financial_data(n_clicks, code, start_date, end_date):
    if not code:
        return html.P("请输入股票代码")

    try:
        data = get_financial_report(
                    symbol=code, 
                    range=DateRangeModel(start=start_date, end=end_date))
        return [
            create_table(data.get("BalanceSheet", []), "资产负债表"),
            create_table(data.get("ProfitSheet", []), "利润表"),
            create_table(data.get("CashFlow", []), "现金流量表"),
        ]

    except Exception as e:
        return html.P(f"请求出错: {e}")
