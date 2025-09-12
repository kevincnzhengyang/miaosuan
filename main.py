'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-23 10:15:30
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 20:25:58
FilePath: /miaosuan2/main.py
Description:  miaosuan cli entry point

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import click, uvicorn, qlib

from config.settings import settings
from localdb.tables import init_db
from backend import fastapi
from frontend import dashapp


@click.command()
# @click.argument('filename')
@click.option('--miaosuan', is_flag=True, help='启动妙算服务')
@click.option('--dashboard', is_flag=True, help='启动工作台')
# def cli(filename, api, mcp):
def cli(miaosuan, dashboard):
    # 初始化数据库
    init_db()
    
    if miaosuan:
        click.echo(f'开启妙算服务')
        
        # 初始化QLib
        qlib.init(provider_uri=settings.DATA_DIR, region="cn")

        # 启动妙算服务
        uvicorn.run(fastapi, 
                    host=settings.API_HOST, 
                    port=settings.API_PORT)
    elif dashboard:
        click.echo(f'开启工作台')
        # 启动工作台界面
        dashapp.run(host=settings.APP_HOST, 
                    port=settings.APP_PORT)
        
    else:
        click.echo(f'没有指定运行模式')
        

if __name__ == '__main__':
    cli()
