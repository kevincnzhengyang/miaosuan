'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-25 22:25:44
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 20:32:15
FilePath: /miaosuan2/services/chuanyin.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

from loguru import logger
from fastapi import APIRouter

from localdb.db_chuanyin import add_subscriber, remove_subscriber, list_subscribers
from helper.telegram_bot import telegram_broadcast
from helper.line_bot import line_broadcast
from datamodels.dm_subscriber import Subscriber, Message


router = APIRouter(
    prefix="/chuanyin",
    tags=["ChuanYin"],
)


@router.post("/subscribe")
async def subscribe(sub: Subscriber):
    add_subscriber(sub.platform, sub.user_id)
    return {"status": "ok", "message": f"{sub.platform}:{sub.user_id} 已订阅"}

@router.delete("/unsubscribe/{user_id}")
async def unsubscribe(user_id: str):
    remove_subscriber(user_id)
    return {"status": "ok", "message": f"{user_id} 已取消订阅"}

@router.get("/subscribers")
async def get_subscribers():
    return list_subscribers()

@router.post("/notify")
async def notify(msg: Message):
    tel_res = await telegram_broadcast(msg)
    line_res = await line_broadcast(msg)
    return {"status": "ok", "telegram": str(tel_res), "line": str(line_res)}
