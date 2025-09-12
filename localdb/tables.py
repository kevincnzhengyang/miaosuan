'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 19:05:41
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 19:45:03
FilePath: /miaosuan2/localdb/tables.py
Description: 初始化数据库表

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os, sqlite3
from loguru import logger

from config.settings import settings

def init_db():
    # 确保数据库文件存在    
    if not os.path.exists(settings.DB_FILE):
        logger.info(f"数据库文件不存在，创建数据库文件：{settings.DB_FILE}")
        with open(settings.DB_FILE, "w") as f:
            f.write("") 
        logger.info(f"数据库文件创建成功：{settings.DB_FILE}")
    else:
        logger.info(f"数据库文件已存在：{settings.DB_FILE}") 
    
    conn = sqlite3.connect(settings.DB_FILE)
    cur = conn.cursor()

    # 创建传音数据表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,   -- "telegram" or "line"
            user_id TEXT NOT NULL UNIQUE
        )
    """)
    
    # 创建谛听数据表
    cur.execute("""CREATE TABLE IF NOT EXISTS rules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE, symbol TEXT NOT NULL, 
        brokers TEXT NOT NULL, rule_json TEXT NOT NULL,
        webhook_url TEXT NOT NULL, tag TEXT NOT NULL,
        note TEXT, enabled INTEGER DEFAULT 1, 
        updated_at TIMESTAMP
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS triggers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_id INTEGER NOT NULL,
        symbol TEXT, message TEXT,
        ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(rule_id) REFERENCES rules(id)
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rules_symbol ON rules(symbol)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rules_enabled ON rules(enabled)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_triggers_rule_id ON triggers(rule_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_triggers_symbol ON triggers(symbol)")
    
    
    # 创建千手数据表
    cur.execute("""CREATE TABLE IF NOT EXISTS equities(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL UNIQUE, market TEXT NOT NULL, 
        note TEXT, enabled INTEGER DEFAULT 1, 
        last_date TIMESTAMP, updated_at TIMESTAMP
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_equities_symbol ON equities(symbol)")
    conn.commit()
    conn.close()
    logger.info(f"初始化数据库 {settings.DB_FILE}")
