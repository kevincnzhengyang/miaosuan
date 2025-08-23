'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 10:15:30
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-23 14:06:49
FilePath: /mss_diting/app/main.py
Description:  diting cli entry point

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import os, click, asyncio
import uvicorn
from loguru import logger
from dotenv import load_dotenv
from diting.db_sqlite import init_db
from diting.mode_api import api as fastapi
from diting.mode_mcp import mcp as mcpserver
from diting.futu_task import start_futu_task

# 加载环境变量
load_dotenv()
LOG_FILE = os.getenv("LOG_FILE", "diting.log")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "21000"))

# 记录日志到文件，日志文件超过500MB自动轮转
logger.add(LOG_FILE, rotation="50 MB")


@click.command()
# @click.argument('filename')
@click.option('--api', is_flag=True, help='启动API服务')
@click.option('--mcp', is_flag=True, help='启动MCP服务')
# def cli(filename, api, mcp):
async def cli(api, mcp):
    # 初始化数据库
    init_db()
    await start_futu_task()

    if api:
        click.echo(f'API模式开启')
        uvicorn.run(fastapi, host=API_HOST, port=API_PORT)
    elif mcp:
        click.echo(f'MCP模式开启')
        mcpserver.run()
    else:
        click.echo(f'没有指定运行模式')


if __name__ == '__main__':
    cli()
