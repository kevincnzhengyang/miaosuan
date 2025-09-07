'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 12:00:17
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-04 19:50:55
FilePath: /mss_diting/app/diting/db_sqlite.py
Description: Sqlite数据库操作

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import os, json, sqlite3
from pathlib import Path
from typing import Any
from loguru import logger
from dotenv import load_dotenv

from .models import Rule, Trigger
from .quote_rule import validate_rule


# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".." / ".env")
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
    # 提交事务并关闭连接
    conn.commit()
    conn.close()
    logger.info("数据库初始化完成")

def add_rule(rule: Rule) -> Any:
    # 插入数据库前校验规则
    validate_rule(json.loads(rule.rule_json)) 

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO rules(name,symbol,brokers,rule_json,webhook_url,tag,note,enabled,updated_at) VALUES(?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                (rule.name, rule.symbol, rule.brokers, rule.rule_json, rule.webhook_url, rule.tag, rule.note, int(rule.enabled)))
    conn.commit()
    rule_id = cur.lastrowid
    conn.close()
    return rule_id

def get_rules(only_valid: bool = True) -> list[Any]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    if only_valid:
        rows = conn.execute("SELECT * FROM rules WHERE enabled=1").fetchall()
    else:
        rows = conn.execute("SELECT * FROM rules").fetchall()
    conn.close()
    return rows

def get_updated_rules(since: str) -> list[Any]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM rules WHERE updated_at > ? AND enabled=1", (since,)).fetchall()
    conn.close()
    return rows

def get_rules_by_symbol(symbol: str, only_valid: bool = True) -> list[Any]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    if only_valid:
        rows = conn.execute("SELECT * FROM rules WHERE symbol=? AND enabled=1", (symbol,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM rules WHERE symbol=?", (symbol,)).fetchall()
    conn.close()
    return rows

def get_rule(rule_id: int) -> Any:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM rules WHERE id=?", (rule_id,)).fetchone()
    conn.close()
    return row

def update_rule(rule_id: int, rule: Rule) -> Any:
    # 插入数据库前校验规则
    validate_rule(json.loads(rule.rule_json)) 
    
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE rules SET name=?,symbol=?,brokers=?,rule_json=?,webhook_url=?,tag=?,note=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                 (rule.name, rule.symbol, rule.brokers, rule.rule_json, rule.webhook_url, rule.tag, rule.note, rule_id))
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
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM triggers ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return rows

def get_triggers_by_rule_id(rule_id: int, limit: int = 100) -> list[Any]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM triggers WHERE rule_id=? ORDER BY ts DESC LIMIT ?", (rule_id, limit)).fetchall()
    conn.close()
    return rows

def get_triggers_by_symbol(symbol: str, limit: int = 100) -> list[Any]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
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
