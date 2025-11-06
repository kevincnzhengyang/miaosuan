'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-01 10:23:51
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-11-06 10:02:17
FilePath: /miaosuan/helper/bin_tools.py
Description: QLib BIN文件工具

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import os, sys
import pandas as pd
from loguru import logger
from pathlib import Path
from datetime import date
from qlib.data import D

from config.settings import settings
from localdb.db_qianshou import get_equity_by_symbol
from datamodels.dm_equity import Equity


def convert_csv_to_bin() -> None:
    # 准备导出BIN格式的工具脚本
    sys.path.append(os.path.join(settings.QLIB_DIR, "scripts"))
    from dump_bin import DumpDataAll  # type: ignore warnings

    # 转换为Qlib的BIN格式
    dump = DumpDataAll(
        data_path=settings.CSV_DIR,
        qlib_dir=settings.DATA_DIR,
        exclude_fields="date,symbol")
    dump.dump()
    logger.info(f"将数据由CSV转换为BIN")

def _get_all_qlib_fields(data_dir: str, code: str) -> list:
    """
    扫描 Qlib 数据目录，返回所有已存储的 field 名称（含自定义指标）
    :param provider_uri: qlib.init 使用的 provider_uri 目录 (例如 ~/.qlib/qlib_data/cn_data)
    :return: list[str] 字段名列表
    """
    root = Path(os.path.join(data_dir, "features", code.lower()))
    if not root.exists():
        logger.error(f"目录不存在: {root}")
        return []

    bin_files = list(root.rglob("*.bin"))
    if not bin_files:
        logger.error(f"在 {root} 下未找到任何 .bin 文件")
        return []

    def field_from_filename(fname: str):
        # 例子: rsi14.day.bin -> rsi14
        parts = Path(fname).name.split(".")
        if len(parts) >= 3:
            return ".".join(parts[:-2])  # 去掉 freq + bin
        return parts[0].replace(".bin", "")

    fields_set = { field_from_filename(p.name) for p in bin_files }
    return [f"${f.upper()}" for f in sorted(fields_set)]

def load_equity_quote(symbol: str, start_date: date, end_date: date) -> list:
    res = []

    row = get_equity_by_symbol(symbol=symbol)
    if row is None:
        logger.error(f"找不到股票{symbol}，无法获得财务数据")
        return res
    
    e = Equity(**row)
    ft_name = e.to_futu_symbol()
    logger.debug(f"找到股票{e.symbol}")

    fields = _get_all_qlib_fields(settings.DATA_DIR, ft_name)
    if not fields:
        return res
    
    df = D.features(
        instruments=[ft_name], 
        fields=fields,                 # ⭐ 一次性取所有字段
        start_time=start_date, 
        end_time=end_date,
        disk_cache=0                # ⭐ 关闭磁盘缓存，避免重复读取同一文件
    )
    if df is None or not isinstance(df, pd.DataFrame) or len(df) == 0:
        return res
    df = df.replace({float('nan'): None}).reset_index()
    df['date'] = df['datetime'].dt.date
    df.drop(columns=['instrument', 'datetime'], inplace=True)
    return df.to_dict(orient="records")
