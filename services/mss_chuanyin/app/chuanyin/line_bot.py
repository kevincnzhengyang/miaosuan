'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-25 23:06:13
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-26 18:34:20
FilePath: /mss_chuanyin/app/chuanyin/line_bot.py
Description: line bot integration

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import os, asyncio, httpx
from loguru import logger
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import FlexSendMessage

from .sqlite_db import list_subscribers
from .models import Message

# 加载环境变量
load_dotenv(dotenv_path="../.env")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN", "")


line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

async def send_to_line(user_id: str, fmsg: FlexSendMessage):
    try:
        line_bot_api.push_message(
            to=user_id,
            messages=fmsg
        )
        logger.info(f"Sent message to LINE user {user_id}")
    except Exception as e:
        logger.error(f"Error sending message to LINE user {user_id}: {e}")
    

# 广播消息给所有订阅用户
async def line_broadcast(msg: Message):
    arrow = "🟢" if msg.ohlc['pct_chg'] < 0 else "🔴"

    flex_message = FlexSendMessage(
        alt_text="行情推送",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    { "type": "text", "text": f"{msg.tag}=={msg.name}", "weight": "bold", "size": "lg" },
                    { "type": "text", "text": f"🏷 股票: {msg.symbol}", "size": "md" },
                    { "type": "text", "text": f"🛎 开盘: {msg.ohlc['open']}" },
                    { "type": "text", "text": f"🔔 收盘: {msg.ohlc['close']}" },
                    { "type": "text", "text": f"🔼 最高: {msg.ohlc['high']}" },
                    { "type": "text", "text": f"🔽 最低: {msg.ohlc['low']}" },
                    { "type": "text", "text": f"💰 成交量: {msg.ohlc['volume']}" },
                    { "type": "text", "text": f"{arrow} 涨跌幅: {msg.ohlc['pct_chg']}" },
                    { "type": "text", "text": f"🌊 振幅: {msg.ohlc['pct_amp']}" }
                ]
            }
        }
    )

    logger.info(f"Broadcasting message to Telegram subscribers: {flex_message}")
    subs = list_subscribers("line")
    tasks = [send_to_line(
                user_id=sub["user_id"], 
                fmsg=flex_message) for sub in subs]
    return await asyncio.gather(*tasks, return_exceptions=True)
