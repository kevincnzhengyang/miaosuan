'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 12:34:08
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-23 13:51:46
FilePath: /mss_diting/app/diting/mode_mcp.py
Description: MCP模式

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

from mcp.server.fastmcp import FastMCP  # MCP adapter
from loguru import logger
from .models import Rule, Trigger

from .db_sqlite import *


mcp = FastMCP("futu-signal-service")

@mcp.tool()
def mcp_add_rule(symbol: str, condition: str, threshold: float, webhook_url: str,
                 cooldown_sec: int=60, note: str="", enabled: bool=True):
    """通过 MCP 添加规则"""
    return add_rule(Rule(symbol=symbol, condition=condition, threshold=threshold,
                         webhook_url=webhook_url, cooldown_sec=cooldown_sec, note=note, enabled=enabled))

@mcp.tool()
def mcp_list_rules():
    """通过 MCP 列出规则"""
    return get_rules()

@mcp.tool()
def mcp_list_triggers():
    """通过 MCP 获取触发日志"""
    return get_triggers()

