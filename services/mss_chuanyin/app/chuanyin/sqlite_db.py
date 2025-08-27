'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-25 22:55:10
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-27 21:01:38
FilePath: /mss_chuanyin/app/chuanyin/sqlite_db.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os, sqlite3
from loguru import logger
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".." / ".env")
DB_FILE = os.getenv("DB_FILE", "chuanyin.db")


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,   -- "telegram" or "line"
            user_id TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()
    logger.info(f"Initialized database at {DB_FILE}")

def add_subscriber(platform: str, user_id: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO subscribers (platform, user_id) VALUES (?, ?)", (platform, user_id))
        conn.commit()
    finally:
        conn.close()
    logger.info(f"Added subscriber: platform={platform}, user_id={user_id}")

def remove_subscriber(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM subscribers WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    logger.info(f"Removed subscriber: user_id={user_id}")

def list_subscribers(platform: str|None = None):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if platform:
        c.execute("SELECT platform, user_id FROM subscribers WHERE platform=?", (platform,))
    else:
        c.execute("SELECT platform, user_id FROM subscribers")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

