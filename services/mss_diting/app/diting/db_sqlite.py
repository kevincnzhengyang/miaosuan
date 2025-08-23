'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 12:00:17
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-23 13:46:05
FilePath: /mss_diting/app/diting/db_sqlite.py
Description: Sqlite数据库操作

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import sqlite3
import os
from typing import Any
from loguru import logger
from dotenv import load_dotenv

from .models import Rule, Trigger


# 加载环境变量
load_dotenv(dotenv_path="../.env")
DB_FILE = os.getenv("DB_FILE", "diting.db")

# 初始化数据库
def init_db():
    # 确保数据库文件存在    
    if not os.path.exists(DB_FILE):
        logger.info(f"数据库文件不存在，创建数据库文件：{DB_FILE}")
        with open(DB_FILE, "w") as f:
            f.write("") 
        logger.info(f"数据库文件创建成功：{DB_FILE}")
    else:
        logger.info(f"数据库文件已存在：{DB_FILE}") 
    
    # 连接数据库
    conn = sqlite3.connect(DB_FILE)
    # 创建游标
    cur = conn.cursor()

    # 创建表
    cur.execute("""CREATE TABLE IF NOT EXISTS rules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT, condition TEXT, threshold REAL,
        webhook_url TEXT, cooldown_sec INTEGER, brokers TEXT, 
        note TEXT, enabled INTEGER, updated_at TIMESTAMP
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS triggers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_id INTEGER REFERENCES rules(id),
        symbol TEXT, message TEXT,
        ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()
    logger.info("数据库初始化完成")

def add_rule(rule: Rule) -> Any:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO rules(symbol,condition,threshold,webhook_url,cooldown_sec,note,enabled,updated_at) VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                (rule.symbol, rule.condition, rule.threshold, rule.webhook_url, rule.cooldown_sec, rule.note, int(rule.enabled)))
    conn.commit()
    rule_id = cur.lastrowid
    conn.close()
    return rule_id

def get_rules() -> list[Any]:
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT * FROM rules").fetchall()
    conn.close()
    return rows

def get_rules_by_symbol(symbol: str, only_valid: bool = True) -> list[Any]:
    conn = sqlite3.connect(DB_FILE)
    if only_valid:
        rows = conn.execute("SELECT * FROM rules WHERE symbol=? AND enabled=1", (symbol,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM rules WHERE symbol=?", (symbol,)).fetchall()
    conn.close()
    return rows

def get_rule(rule_id: int) -> Any:
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute("SELECT * FROM rules WHERE id=?", (rule_id,)).fetchone()
    conn.close()
    return row

def update_rule(rule_id: int, rule: Rule) -> Any:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE rules SET symbol=?,condition=?,threshold=?,webhook_url=?,cooldown_sec=?,note=?,enabled=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                 (rule.symbol, rule.condition, rule.threshold, rule.webhook_url, rule.cooldown_sec, rule.note, int(rule.enabled), rule_id))
    conn.commit()
    conn.close()
    return rule_id

def delete_rule(rule_id: int) -> None:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE rules SET enabled=0 WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()

def purge_rule(rule_id: int) -> None:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM rules WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()

def add_trigger(trigger: Trigger) -> Any:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO triggers(rule_id,symbol,message) VALUES(?,?,?)",
                (trigger.rule_id, trigger.symbol, trigger.message))
    conn.commit()
    trigger_id = cur.lastrowid
    conn.close()
    return trigger_id

def get_triggers(limit: int = 100) -> list[Any]:
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT * FROM triggers ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return rows

def get_triggers_by_rule_id(rule_id: int, limit: int = 100) -> list[Any]:
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT * FROM triggers WHERE rule_id=? ORDER BY ts DESC LIMIT ?", (rule_id, limit)).fetchall()
    conn.close()
    return rows

def get_triggers_by_symbol(symbol: str, limit: int = 100) -> list[Any]:
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT * FROM triggers WHERE symbol=? ORDER BY ts DESC LIMIT ?", (symbol, limit)).fetchall()
    conn.close()
    return rows

def delete_trigger(trigger_id: int) -> None:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM triggers WHERE id=?", (trigger_id,))
    conn.commit()
    conn.close()

def clear_triggers() -> None:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM triggers")
    conn.commit()
    conn.close()
