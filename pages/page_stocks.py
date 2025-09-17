'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-10 19:43:10
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-17 11:24:28
FilePath: /miaosuan2/pages/page_stocks.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import dash
from dash import html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc

from pages.api_client import get_stock_list


dash.register_page(__name__, path="/", name="关注股票")


stock_data = get_stock_list()

# 构造表格数据
table_data = []
for i, stock in enumerate(stock_data):
    row = {
        "代码": stock.get("symbol"),
        "名称": stock.get("name"),
        "市场": stock.get("market"),
        "简介": "[查看]()",
    }
    table_data.append(row)

layout = dbc.Container([
    html.H2("关注股票", className="my-3"),
    dash_table.DataTable(
        id="stock-table",
        columns=[
            # {"name": "", "id": "logo", "presentation": "markdown"},
            {"name": "代码", "id": "代码", },
            {"name": "名称", "id": "名称"},
            {"name": "市场", "id": "市场"},
            {"name": "简介", "id": "简介", "presentation": "markdown"},
        ],
        data=table_data,
        filter_action="native",  # 全局启用列筛选
        sort_action="native",    # 全局启用排序
        page_action="native",
        page_size=10,
        style_cell={  # 默认样式
            "padding": "10px",
            "font-family": "Arial, sans-serif",
            "font-size": "14px",
            "textAlign": "center",   # 默认居中
            "lineHeight": "1.2",     # 行间距
        },
        style_data_conditional=[  # 第一列右对齐
            {
                "if": {"column_id": "代码"},
                "textAlign": "right",    # type: ignore
            }
        ],
        style_header={
            "backgroundColor": "#f8f9fa",
            "fontWeight": "bold",
            "border-bottom": "2px solid #dee2e6",
            "font-size": "15px",
            "textAlign": "center",
        },
        style_table={"overflowX": "auto"},
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("详情")),
            dbc.ModalBody(id="modal-body"),
            dbc.ModalFooter(
                dbc.Button("关闭", id="close-modal", n_clicks=0, className="ms-auto")
            ),
        ],
        id="stock-modal",
        size="lg",
        is_open=False,
    )
], fluid=True)

# 回调处理点击“查看”
@callback(
    Output("stock-modal", "is_open"),
    Output("modal-body", "children"),
    Input("stock-table", "active_cell"),
    Input("close-modal", "n_clicks"),
    State("stock-modal", "is_open"),
    prevent_initial_call=True
)
def open_modal(active_cell, close_click, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "stock-table" and active_cell:
        row_idx = active_cell["row"]
        col_id = active_cell["column_id"]
        stock = stock_data[row_idx]
        if col_id == "简介":
            notes = stock.get("note", [])
            if isinstance(notes, list):
                if notes and isinstance(notes[0], dict):
                    body = html.Ul([html.Li(f"{n.get('item')}: {n.get('value')}") for n in notes])
                else:
                    body = html.Ul([html.Li(str(n)) for n in notes])
            else:
                body = html.P("无简介信息")
            return True, body
        elif col_id == "财报":
            return True, html.P("财报页面内容占位")
        elif col_id == "分析":
            return True, html.P("量化分析内容占位")

    elif trigger_id == "close-modal" and close_click:
        return False, dash.no_update

    return is_open, dash.no_update
