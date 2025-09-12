'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 12:33:59
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 20:34:46
FilePath: /miaosuan2/services/diting.py
Description: API模式

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

from loguru import logger
from fastapi import APIRouter

from localdb.db_diting import *
from .mss_diting.quote_manager import manager


router = APIRouter(
    prefix="/diting",
    tags=["DiTing"],
)


@router.get("/rules")
def list_rules_api():
    rows = get_rules()
    return rows

@router.get("/rules/symbol/{symbol}")
def get_rules_by_symbol_api(symbol: str, only_valid: bool = True):
    rows = get_rules_by_symbol(symbol, only_valid)
    return rows

@router.post("/rules")
def add_rule_api(rule: Rule):
    rid = add_rule(rule)
    logger.info(f"添加规则，ID={rid}")
    return {"status":"ok", "id": rid}

@router.get("/rules/{rule_id}")
def get_rule_by_id_api(rule_id: int):
    row = get_rule(rule_id)
    return row

@router.put("/rules/{rule_id}")
def update_rule_by_id_api(rule_id: int, rule: Rule):
    update_rule(rule_id, rule)
    logger.info(f"更新规则，ID={rule_id}")
    return {"status":"ok"}

@router.delete("/rules/{rule_id}")
def delete_rule_by_id_api(rule_id: int):
    delete_rule(rule_id)
    logger.info(f"删除规则，ID={rule_id}")
    return {"status":"ok"}  

@router.get("/triggers")
def list_triggers_api():
    rows = get_triggers()
    return rows

@router.get("/triggers/symbol/{symbol}")
def get_triggers_by_symbol_api(symbol: str):
    rows = get_triggers_by_symbol(symbol)
    return rows

@router.get("/triggers/rule/{rule_id}")
def get_triggers_by_rule_api(rule_id: int):
    rows = get_triggers_by_rule_id(rule_id)
    return rows

@router.get("/engine/status")
def engine_status_api():
    status = manager.status()
    return status
