'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 19:35:18
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 19:35:58
FilePath: /miaosuan2/localdb/db_chuanyin.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import sqlite3
from loguru import logger

from config.settings import settings


def add_subscriber(platform: str, user_id: str):
    conn = sqlite3.connect(settings.DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO subscribers (platform, user_id) VALUES (?, ?)", (platform, user_id))
        conn.commit()
    finally:
        conn.close()
    logger.info(f"Added subscriber: platform={platform}, user_id={user_id}")

def remove_subscriber(user_id: str):
    conn = sqlite3.connect(settings.DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM subscribers WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    logger.info(f"Removed subscriber: user_id={user_id}")

def list_subscribers(platform: str|None = None):
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if platform:
        c.execute("SELECT platform, user_id FROM subscribers WHERE platform=?", (platform,))
    else:
        c.execute("SELECT platform, user_id FROM subscribers")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
