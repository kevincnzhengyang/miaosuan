import dash, requests, json
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc

# ============= 1. 启动 Dash 应用，加载 Bootstrap 方便 Modal 窗口 ============
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# ============= 2. 通过 API 获取数据 ============
API_URL = "http://192.168.3.3:23000/equities"

def fetch_stock_data():
    try:
        resp = requests.get(API_URL, timeout=5)
        if resp.status_code == 200:
            stocks = []
            for s in  resp.json():
                s['note']=json.loads(s['note'])
                stocks.append(s)
            return stocks
        else:
            return []
    except Exception as e:
        print("Error fetching data:", e)
        return []

stock_data = fetch_stock_data()

# 格式化 DataTable 的数据
table_data = []
for i, stock in enumerate(stock_data):
    row = {
        "代码": stock.get("symbol"),
        "名称": stock.get("name"),
        "市场": stock.get("market"),
        "简介": "[查看]()",
        "财报": "[打开]()",
        "分析": "[打开]()",
    }
    table_data.append(row)

# ============= 3. 定义 Dash Layout ============
app.layout = dbc.Container([
    html.H2("关注股票", className="my-3"),

    dash_table.DataTable(
        id="stock-table",
        columns=[
            {"name": "代码", "id": "代码"},
            {"name": "名称", "id": "名称"},
            {"name": "市场", "id": "市场"},
            {"name": "简介", "id": "简介", "presentation": "markdown"},
            {"name": "财报", "id": "财报", "presentation": "markdown"},
            {"name": "分析", "id": "分析", "presentation": "markdown"},
        ],
        data=table_data,
        style_cell={"textAlign": "center"},
        style_table={"overflowX": "auto"},
    ),

    # 弹窗
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("股票简介")),
            dbc.ModalBody(id="modal-body"),
            dbc.ModalFooter(
                dbc.Button("关闭", id="close-modal", className="ms-auto", n_clicks=0)
            ),
        ],
        id="stock-modal",
        size="lg",
        is_open=False,
    ),
], fluid=True)

# ============= 4. 交互逻辑 ============
@app.callback(
    Output("stock-modal", "is_open"),
    Output("modal-body", "children"),
    Input("stock-table", "active_cell"),
    Input("close-modal", "n_clicks"),
    State("stock-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_modal(active_cell, close_click, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # 点击表格中的 "简介"
    if trigger_id == "stock-table" and active_cell:
        row_idx = active_cell["row"]
        col_id = active_cell["column_id"]

        if col_id == "简介":
            stock = stock_data[row_idx]
            notes = stock.get("note", [])

            if isinstance(notes, list):
                if notes and isinstance(notes[0], dict):
                    body = html.Ul([
                        html.Li(f"{n.get('item')}: {n.get('value')}") for n in notes
                    ])
                else:
                    body = html.Ul([html.Li(str(n)) for n in notes])
            else:
                body = html.P("无简介信息")

            return True, body

    # 点击关闭按钮
    elif trigger_id == "close-modal" and close_click:
        return False, dash.no_update

    return is_open, dash.no_update


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8050)
