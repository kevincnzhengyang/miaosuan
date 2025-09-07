'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-07 10:34:42
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-07 12:13:25
FilePath: /miaosuan/app/main.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio, json
from app.websocket import manager, periodic_broadcast
from app.tasks import list_tasks
from app.api_client import get_stock_list, get_financial_report

app = FastAPI(title="量化多任务 Dashboard")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# 启动后台广播任务
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_broadcast())

@app.get("/")
async def index():
    tasks = list_tasks()
    return {"tasks": tasks}

@app.websocket("/ws/{window_id}/{task_id}")
async def websocket_endpoint(websocket: WebSocket, window_id: str, task_id: str):
    await manager.connect(window_id, task_id, websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            try:
                data = json.loads(msg)
                if "last_time" in data:
                    manager.active_windows[window_id]["last_time"] = data["last_time"]
            except:
                continue
    except:
        manager.disconnect(window_id)
# ----------------------------
# 股票列表页面
# ----------------------------
@app.get("/stocks")
async def stocks_page(request: Request):
    stocks = get_stock_list()
    return templates.TemplateResponse("stocks.html", {"request": request, "stocks": stocks})

# ----------------------------
# 财报页面
# ----------------------------
@app.get("/financials/{symbol}")
async def financials_page(request: Request, symbol: str):
    balance_sheet = get_financial_report(symbol, "balance_sheet")
    income_statement = get_financial_report(symbol, "income_statement")
    cash_flow = get_financial_report(symbol, "cash_flow")
    return templates.TemplateResponse("financials.html", {
        "request": request,
        "symbol": symbol,
        "balance_sheet": balance_sheet,
        "income_statement": income_statement,
        "cash_flow": cash_flow
    })

# ----------------------------
# 回测对比页面
# ----------------------------
@app.get("/compare")
async def compare_page(request: Request):
    # 前端 WebSocket 会加载 compare.html
    return templates.TemplateResponse("compare.html", {"request": request})
