'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-07 11:01:53
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-07 11:02:46
FilePath: /miaosuan/qianji/core/data_manager.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os
import pandas as pd
from pathlib import Path
import shutil
import datetime

RAW_DIR = "data/raw"
ARTIFACT_DIR = "artifacts"

class DataManager:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.task_path = Path(ARTIFACT_DIR)/task_id
        self.task_path.mkdir(parents=True, exist_ok=True)

    def load_bin(self, symbol: str):
        # 假设 QLib BIN 数据转换成 Parquet
        bin_path = Path(RAW_DIR)/f"{symbol}.bin"
        if not bin_path.exists():
            raise FileNotFoundError(f"{bin_path} not found")
        df = pd.read_parquet(bin_path)
        return df

    def save_artifact(self, name: str, df: pd.DataFrame):
        path = self.task_path/f"{name}.parquet"
        df.to_parquet(path)
        return path

    def save_metrics(self, metrics: dict):
        import json
        path = self.task_path/"stats.json"
        with open(path,"w") as f:
            json.dump(metrics,f,indent=4)
        return path

    def backup_task(self):
        version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = Path(ARTIFACT_DIR)/f"{self.task_id}_{version}"
        shutil.copytree(self.task_path, backup_path)
        return backup_path
