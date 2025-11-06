'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-25 22:51:51
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-11-06 11:24:17
FilePath: /miaosuan/helper/telegram_bot.py
Description: Telegram bot integration

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import os, asyncio
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from telegram import Bot

from config.settings import settings
from localdb.db_chuanyin import list_subscribers
from datamodels.dm_subscriber import Message


telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN) # type: ignore

# 广播消息给所有订阅用户
async def telegram_broadcast(msg: Message):
    arrow = "🟢" if msg.ohlc['pct_chg'] < 0 else "🔴"
    text = (
        f"* {msg.tag}\\=\\=\\={msg.name} *\n"
        f"🏷 股票: `{msg.symbol}`\n"
        f"🛎 开盘: `{msg.ohlc['open']}`\n"
        f"🔔 收盘: `{msg.ohlc['close']}`\n"
        f"🔼 最高: `{msg.ohlc['high']}`\n"
        f"🔽 最低: `{msg.ohlc['low']}`\n"
        f"💰 成交量: `{msg.ohlc['volume']}`\n"
        f"{arrow} 涨跌幅: `{msg.ohlc['pct_chg']:.2f}%`\n"
        f"🌊 振幅: `{msg.ohlc['pct_amp']:.2f}%`"
    )
    
    # logger.info(f"Broadcasting message to Telegram subscribers: {text}")
    subs = list_subscribers("telegram")
    if subs is None or len(subs) == 0:
        logger.warning("没有Teleram订阅用户")
        return
    tasks = [telegram_bot.send_message(
                chat_id=sub["user_id"], 
                text=text,
                parse_mode="MarkdownV2") for sub in subs]
    return await asyncio.gather(*tasks, return_exceptions=True)

# 广播图片给所有订阅用户
async def telegram_broadcast_image(img: str, caption: str):
    with open(img, "rb") as photo:
        subs = list_subscribers("telegram")
        if subs is None or len(subs) == 0:
            logger.warning("没有Teleram订阅用户")
            return
        tasks = [telegram_bot.send_photo(
                    chat_id=sub["user_id"], 
                    photo=photo,
                    caption=caption) for sub in subs]
        await asyncio.gather(*tasks, return_exceptions=True)

async def telegram_broadcast_report(text: str):    
    # logger.info(f"Broadcasting message to Telegram subscribers: {text}")
    subs = list_subscribers("telegram")
    if subs is None or len(subs) == 0:
        logger.warning("没有Teleram订阅用户")
        return
    tasks = [telegram_bot.send_message(
                chat_id=sub["user_id"], 
                text=text,
                parse_mode="MarkdownV2") for sub in subs]
    return await asyncio.gather(*tasks, return_exceptions=True)
