'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 18:31:43
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-15 11:30:30
FilePath: /miaosuan2/services/mss_qianji/data_manager.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os
import pandas as pd
from pathlib import Path
from qlib.data import D


class DataManager:
    def __init__(self, data_dir: str, recs_dir: str):
        self.data_dir = data_dir
        self.recs_dir = recs_dir
        self.task_dir = ""
    
    def _get_all_fields(self, instrument: str) -> list:
        root = Path(os.path.join(self.data_dir, "features", instrument.lower()))
        if not root.exists():
            raise FileNotFoundError(f"目录不存在: {root}")

        bin_files = list(root.rglob("*.bin"))
        if not bin_files:
            raise RuntimeError(f"在 {self.data_dir} 下未找到任何 .bin 文件")

        def field_from_filename(fname: str):
            # 例子: rsi14.day.bin -> rsi14
            parts = Path(fname).name.split(".")
            if len(parts) >= 3:
                return ".".join(parts[:-2])  # 去掉 freq + bin
            return parts[0].replace(".bin", "")

        fields_set = {field_from_filename(p.name) for p in bin_files}

        # 处理基础行情字段，统一用 Qlib 规范
        normalized_fields = []
        for f in sorted(fields_set):
            normalized_fields.append(f"${f.upper()}")
        return normalized_fields
    
    def set_task_id(self, task_id: str):
        self.task_dir = os.path.join(self.recs_dir, task_id)
        os.makedirs(self.task_dir, exist_ok=True)

    def load_market_data(self, instrument: str, 
                         start_time: str, end_time: str,
                         fields: list|None = None):
        if fields is None:
            fields = self._get_all_fields(instrument)
        df = D.features(instruments=[instrument], 
                        fields=fields, 
                        start_time=start_time, 
                        end_time=end_time)
        return df

    def save_to_parquet(self, df: pd.DataFrame, name: str):
        df.to_parquet(os.path.join(self.task_dir, f"{name}.parquet"))
