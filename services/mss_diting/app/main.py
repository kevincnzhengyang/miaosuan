'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 10:15:30
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-23 12:46:38
FilePath: /mss_diting/app/main.py
Description:  diting cli entry point

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import os, click
from loguru import logger
from dotenv import load_dotenv
from diting.db_sqlite import init_db

# 加载环境变量
load_dotenv()
LOG_FILE = os.getenv("LOG_FILE", "diting.log")

# 记录日志到文件，日志文件超过500MB自动轮转
logger.add(LOG_FILE, rotation="50 MB")


@click.command()
# @click.argument('filename')
@click.option('--api', is_flag=True, help='启动API服务')
@click.option('--mcp', is_flag=True, help='启动MCP服务')
# def cli(filename, api, mcp):
def cli(api, mcp):
    # 初始化数据库
    init_db()

    if api:
        click.echo(f'API模式开启')
    elif mcp:
        click.echo(f'MCP模式开启')
    else:
        click.echo(f'没有指定运行模式')


if __name__ == '__main__':
    cli()
