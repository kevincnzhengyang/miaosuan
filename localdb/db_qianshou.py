'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 19:45:28
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 21:22:08
FilePath: /miaosuan2/localdb/db_qianshou.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''


import os, sqlite3
from typing import Any
from loguru import logger

from config.settings import settings
from datamodels.dm_equity import Equity

def add_equity(e: Equity) -> Any:
    conn = sqlite3.connect(settings.DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO equities(symbol,market,note,enabled,updated_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP)",
                (e.symbol.upper(), e.market.upper(), e.note, int(e.enabled)))
    conn.commit()
    rule_id = cur.lastrowid
    conn.close()
    return rule_id

def get_equities(only_valid: bool = True) -> list[Any]:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    if only_valid:
        rows = conn.execute("SELECT * FROM equities WHERE enabled=1").fetchall()
    else:
        rows = conn.execute("SELECT * FROM equities").fetchall()
    conn.close()
    return rows

def get_equity(e_id: int) -> Any:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM equities WHERE id=?", (e_id,)).fetchone()
    conn.close()
    return row

def get_equity_by_symbol(symbol: str) -> Any:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM equities WHERE symbol=?", (symbol.upper(),)).fetchone()
    conn.close()
    return row

def if_not_exist_equity(symbol: str) -> bool:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM equities WHERE symbol=?", (symbol.upper(),)).fetchone()
    conn.close()
    return (row is None)

def update_equity(e_id: int, e: Equity) -> Any:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.execute("UPDATE equities SET symbol=?,market=?,note=?,enabled=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                 (e.symbol.upper(), e.market.upper(), e.note, int(e.enabled), e_id))
    conn.commit()
    conn.close()
    return e_id

def set_equities_last() -> Any:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.execute("UPDATE equities SET last_date=CURRENT_TIMESTAMP WHERE enabled=1")
    conn.commit()
    conn.close()

def delete_equity(rule_id: int) -> None:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.execute("UPDATE equities SET enabled=0 WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()

def purge_equity(rule_id: int) -> None:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.execute("DELETE FROM equities WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()
