'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 12:34:08
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-25 17:52:25
FilePath: /mss_diting/app/diting/mode_mcp.py
Description: MCP模式

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import json
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool

from .quote_manager import manager
from .db_sqlite import *

mcp = FastMCP("quote-service")


# ---------------- MCP 工具 ----------------
@mcp.tool()
def mcp_add_rule(name: str, symbol: str, 
                 brokers: str, rule_json: str,
                 webhook_url: str, tag: str,
                 note: str="", enabled: bool=True):
    """通过 MCP 添加规则"""
    return add_rule(Rule(name=name, symbol=symbol, 
                         brokers=brokers, rule_json=rule_json,
                         webhook_url=webhook_url, tag=tag, 
                         note=note, enabled=enabled))

@mcp.tool()
def mcp_list_rules():
    """通过 MCP 列出规则"""
    return get_rules(only_valid=True)

@mcp.tool()
def mcp_list_triggers():
    """通过 MCP 获取触发日志"""
    return get_triggers()

@mcp.tool()
async def get_engine_status() -> str:
    """获取所有行情引擎的运行状态"""
    return json.dumps(manager.status(), ensure_ascii=False)
