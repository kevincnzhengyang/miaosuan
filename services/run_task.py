'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 18:31:43
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 21:33:49
FilePath: /miaosuan2/services/run_task.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
from loguru import logger
from concurrent.futures import ThreadPoolExecutor

from config.settings import settings
from mss_qianji.workflow import TaskWorkflowQLib
from mss_qianji.task_model import load_tasks


def _execute_task(t):
    TaskWorkflowQLib(settings.DATA_DIR, settings.RECS_DIR).run(
        t['task_id'], t['model'], t['instrument'], 
        t['start'], t['end'])

def run_tasks() -> None:
    res, tasks = load_tasks()
    if not res or 0 == len(tasks):
        logger.error("加载任务文件失败！")
        return
    
    # 多任务并行执行
    with ThreadPoolExecutor(max_workers = len(tasks)) as executor:
        executor.map(_execute_task, tasks)
