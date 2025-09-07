'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-25 22:25:44
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-05 10:17:04
FilePath: /mss_chuanyin/app/main.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import os, uvicorn
from loguru import logger
from dotenv import load_dotenv

from fastapi import FastAPI
from contextlib import asynccontextmanager

from chuanyin.sqlite_db import init_db, add_subscriber, remove_subscriber, list_subscribers
from chuanyin.telegram_bot import telegram_broadcast
from chuanyin.line_bot import line_broadcast
from chuanyin.models import Subscriber, Message

# 加载环境变量
load_dotenv()
LOG_FILE = os.getenv("LOG_FILE", "chuanyin.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "21000"))

# 记录日志到文件，日志文件超过500MB自动轮转
logger.add(LOG_FILE, level=LOG_LEVEL, rotation="50 MB", retention=5)


# ===================
# FastAPI 应用
# ===================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    init_db()
    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan, title="Chuanyin Service")

@app.post("/subscribe")
async def subscribe(sub: Subscriber):
    add_subscriber(sub.platform, sub.user_id)
    return {"status": "ok", "message": f"{sub.platform}:{sub.user_id} 已订阅"}

@app.delete("/unsubscribe/{user_id}")
async def unsubscribe(user_id: str):
    remove_subscriber(user_id)
    return {"status": "ok", "message": f"{user_id} 已取消订阅"}

@app.get("/subscribers")
async def get_subscribers():
    return list_subscribers()

@app.post("/diting")
async def notify(msg: Message):
    tel_res = await telegram_broadcast(msg)
    line_res = await line_broadcast(msg)
    return {"status": "ok", "telegram": str(tel_res), "line": str(line_res)}

if __name__ == '__main__':
    logger.info(f"Starting API server at {API_HOST}:{API_PORT}, logging to {LOG_FILE}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
