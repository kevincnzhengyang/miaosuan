'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-07 10:34:42
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-08 11:22:09
FilePath: /miaosuan/app/main.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os, asyncio, json
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.websocket import manager, periodic_broadcast
from app.tasks import list_tasks
from app.api_client import get_stock_list, get_financial_report

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")
LOG_FILE = os.getenv("LOG_FILE", "dashboard.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
DATA_DIR = os.path.expanduser(os.getenv("DATA_DIR", "~/Quanter/qlib_data"))
RECS_DIR = os.path.join(DATA_DIR, "recs")

# 初始化路径
os.makedirs(RECS_DIR, exist_ok=True)

# 记录日志到文件，日志文件超过500MB自动轮转
logger.add(LOG_FILE, level=LOG_LEVEL, rotation="50 MB", retention=5)

# 定时任务
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    # 启动后台广播任务
    asyncio.create_task(periodic_broadcast())

    # scheduler.add_job(futu_update_daily, "cron", 
    #                 day_of_week="1-5", # 每周二到周六
    #                 hour=CRON_HOUR, minute=CRON_MINUTE,
    #                 id="futu_daily")
    # scheduler.add_job(futu_sync_group, "interval", 
    #                 minutes=SYNC_INTERV_M,
    #                 id="futu_sync")
    scheduler.start()
    yield
    scheduler.shutdown()
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan, title="量化多任务 Dashboard")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/tasks")
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
