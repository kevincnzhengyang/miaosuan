'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 18:31:43
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-17 11:10:44
FilePath: /miaosuan2/services/mss_qianji/workflow.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os
import pandas as pd
from loguru import logger
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from qlib.workflow import R
from qlib.backtest import backtest
from qlib.backtest.executor import SimulatorExecutor

from config.settings import settings
from .factory import ModelFactory
from .data_manager import DataManager
from .task_model import load_tasks


class TaskWorkflowQLib:
    def __init__(self, data_dir: str, recs_dir: str):
        self.dm = DataManager(data_dir, recs_dir)

    def run(self, task_id: str, model_name: str, instrument: str, 
            train_start: str, train_end: str,
            valid_start: str, valid_end: str,
            test_start:str, test_end: str):
        self.dm.set_task_id(task_id=task_id)
        model = ModelFactory.get_model(model_name)

        # 1. 加载市场数据
        df = self.dm.load_market_data(instrument=instrument, 
                                      start_time=train_start, 
                                      end_time=train_end,
                                      fields=model.fields)
        logger.debug(f"加载训练数据成功 {task_id}:{instrument} {train_start}-{train_end}, 总条数 {len(df)}")

        # 2. 模型训练 & 预测
        model.train(df)
        pred_df = model.predict(df)
        logger.debug(f"模型训练完成 {task_id}:{instrument} # {model_name}")

        # TODO 让回测基于指定时间段

        # 3. 构建回测 executor
        executor = SimulatorExecutor(
            time_per_step="day",
            start_time=test_start,
            end_time=test_end,
            generate_portfolio_metrics=True,
        )

        # 4. 回测
        strategy_name = "topk"
        port_metrics, _ = backtest(
            start_time=test_start,
            end_time=test_end,
            strategy=strategy_name,
            executor=executor,
            benchmark="HK.800000",
            account=1e7,
            pos_type="Position"
        )
        logger.debug(f"回测完成 {task_id}:{instrument}")

        # 7. 保存结果和实验记录
        with R.start(experiment_name=task_id):
            self.dm.save_to_parquet(df=pred_df, name="pred")
            R.log_artifact(os.path.join(self.dm.task_dir, "pred.parquet"))
            self.dm.save_to_parquet(df=pd.DataFrame(port_metrics), name="report")
            R.log_artifact(os.path.join(self.dm.task_dir, "report.parquet"))
            R.log_metrics(port_metrics)

        logger.info(f"任务完成 {task_id}:{instrument}\n{port_metrics}")
        return port_metrics

def run_tasks() -> None:
    res, tasks = load_tasks()
    if not res or 0 == len(tasks):
        logger.error("加载任务文件失败！")
        return
    
    # 多任务并行执行
    with ThreadPoolExecutor(max_workers = len(tasks)) as executor:
        for t in tasks:
            run_partial = partial(TaskWorkflowQLib(settings.DATA_DIR, 
                                                   settings.RECS_DIR).run, 
                                task_id=t['task_id'], model_name=t['model'],
                                train_start=t['train_start'], 
                                train_end=t['train_end'],
                                valid_start=t['valid_start'], 
                                valid_end=t['valid_end'],
                                test_start=t['test_start'], 
                                test_end=t['test_end'])
            executor.map(run_partial, t['instrument'].split(","))
