'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-07 10:35:39
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-07 11:09:14
FilePath: /miaosuan/app/websocket.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
from fastapi import WebSocket
import asyncio
import pandas as pd
import json
from app.tasks import load_equity, load_signals

class WindowManager:
    def __init__(self):
        self.active_windows: dict = {}  # window_id -> {task_id, websocket, last_time}

    async def connect(self, window_id: str, task_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_windows[window_id] = {
            "task_id": task_id,
            "websocket": websocket,
            "last_time": None
        }

    def disconnect(self, window_id: str):
        if window_id in self.active_windows:
            del self.active_windows[window_id]

    async def broadcast_time_sync(self):
        if not self.active_windows:
            return

        # 找到全局最小时间
        min_time = None
        for w in self.active_windows.values():
            if w["last_time"]:
                t = w["last_time"]
                min_time = t if min_time is None else min(min_time, t)

        # 遍历所有窗口推送同步数据
        for window_id, info in list(self.active_windows.items()):
            task_id = info["task_id"]
            websocket = info["websocket"]

            try:
                equity_df = load_equity(task_id)
                signals_df = load_signals(task_id)

                if min_time:
                    equity_data = equity_df[equity_df['datetime'] <= min_time].to_dict(orient="records")
                    signals_data = signals_df[signals_df['datetime'] <= min_time].to_dict(orient="records")
                else:
                    equity_data = equity_df.to_dict(orient="records")
                    signals_data = signals_df.to_dict(orient="records")

                payload = {"equity": equity_data, "signals": signals_data}
                await websocket.send_json(payload)

            except Exception as e:
                print(f"Disconnecting window {window_id} due to error: {e}")
                self.disconnect(window_id)

manager = WindowManager()

async def periodic_broadcast(interval: float = 1.0):
    while True:
        await manager.broadcast_time_sync()
        await asyncio.sleep(interval)
