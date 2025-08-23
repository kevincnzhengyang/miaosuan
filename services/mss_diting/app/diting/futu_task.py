'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 14:00:02
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-23 14:05:27
FilePath: /mss_diting/app/diting/futu_task.py
Description: 实时订阅后台任务

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import os, asyncio, requests, sqlite3
from loguru import logger
from dotenv import load_dotenv
from .db_sqlite import *

from futu import OpenQuoteContext


# 加载环境变量
load_dotenv(dotenv_path="../.env")
FUTU_API_HOST = os.getenv("FUTU_API_HOST", "127.0.0.1")
FUTU_API_PORT = int(os.getenv("FUTU_API_PORT", "21111"))

async def start_futu_task():
    ctx = OpenQuoteContext(host=FUTU_API_HOST, port=FUTU_API_PORT)
    while True:
        conn = sqlite3.connect(DB_FILE)
        rules = conn.execute("SELECT * FROM rules WHERE enabled=1").fetchall()
        conn.close()
        if rules:
            symbols = [r[1] for r in rules]
            ret, data = ctx.get_stock_quote(symbols)
            if ret == 0:
                for _, row in data.iterrows():
                    symbol, price = row['code'], row['cur_price']
                    for rule in rules:
                        rid, rsymbol, cond, thr, wh, cooldown, note, enabled, last = rule
                        if rsymbol != symbol: continue
                        fire = (cond=="price_above" and price>thr) or \
                               (cond=="price_below" and price<thr)
                        if fire:
                            # webhook + 记录日志
                            try: requests.post(wh, json={"symbol":symbol,"price":price,"note":note})
                            except: pass
                            conn = sqlite3.connect(DB_FILE)
                            conn.execute("INSERT INTO triggers(rule_id,symbol,message) VALUES(?,?,?)",
                                         (rid, symbol, f"{cond}={thr}, price={price}"))
                            conn.commit(); conn.close()
        await asyncio.sleep(1)

