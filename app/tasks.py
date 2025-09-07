'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-07 10:35:29
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-07 11:08:31
FilePath: /miaosuan/app/tasks.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os, json
import pandas as pd

ARTIFACT_DIR = "artifact"

def get_task_path(task_id: str):
    path = os.path.join(ARTIFACT_DIR, task_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Task {task_id} not found")
    return path

def list_tasks():
    return [d for d in os.listdir(ARTIFACT_DIR) if os.path.isdir(os.path.join(ARTIFACT_DIR,d))]

def load_equity(task_id: str):
    path = os.path.join(get_task_path(task_id), "equity.parquet")
    return pd.read_parquet(path)

def load_signals(task_id: str):
    path = os.path.join(get_task_path(task_id), "signals.parquet")
    return pd.read_parquet(path)
