'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 12:33:59
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-23 13:47:06
FilePath: /mss_diting/app/diting/mode_api.py
Description: API模式

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import sqlite3
from loguru import logger
from fastapi import FastAPI

from .db_sqlite import *


# ---------- FastAPI ----------
api = FastAPI(title="Diting MCP+FastAPI Mixed Service")

@api.get("/rules")
def list_rules():
    rows = get_rules()
    return rows

@api.get("/rules/symbol/{symbol}")
def get_rules_by_symbol_api(symbol: str, only_valid: bool = True):
    rows = get_rules_by_symbol(symbol, only_valid)
    return rows

@api.post("/rules")
def add_rule(rule: Rule):
    rid = add_rule(rule)
    logger.info(f"添加规则，ID={rid}")
    return {"status":"ok", "id": rid}

@api.get("/rules/{rule_id}")
def get_rule_by_id(rule_id: int):
    row = get_rule(rule_id)
    return row

@api.put("/rules/{rule_id}")
def update_rule_by_id(rule_id: int, rule: Rule):
    update_rule(rule_id, rule)
    logger.info(f"更新规则，ID={rule_id}")
    return {"status":"ok"}

@api.delete("/rules/{rule_id}")
def delete_rule_by_id(rule_id: int):
    delete_rule(rule_id)
    logger.info(f"删除规则，ID={rule_id}")
    return {"status":"ok"}  

@api.get("/triggers")
def list_triggers():
    rows = get_triggers()
    return rows

@api.get("/triggers/symbol/{symbol}")
def get_triggers_by_symbol(symbol: str):
    rows = get_triggers_by_symbol(symbol)
    return rows

@api.get("/triggers/rule/{rule_id}")
def get_triggers_by_rule(rule_id: int):
    rows = get_triggers_by_rule_id(rule_id)
    return rows

