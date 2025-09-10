import os
import pandas as pd
from loguru import logger
from qlib.workflow import R
from qlib.backtest import backtest
from qlib.backtest.executor import SimulatorExecutor

from .factory import ModelFactory
from .data_manager import DataManager

class TaskWorkflowQLib:
    def __init__(self, data_dir: str, recs_dir: str):
        self.dm = DataManager(data_dir, recs_dir)

    def run(self, task_id: str, model_name: str, instrument: str, 
            start_time: str, end_time: str):
        self.dm.set_task_id(task_id=task_id)
        # 1. 加载市场数据
        df = self.dm.load_market_data(instrument=instrument, 
                                      start_time=start_time, 
                                      end_time=end_time)
        logger.debug(f"加载数据成功 {task_id}:{instrument} {start_time}-{end_time}, 总条数 {len(df)}")

        # 2. 模型训练 & 预测
        model = ModelFactory.get_model(model_name)
        model.train(df)
        pred_df = model.predict(df)
        logger.debug(f"模型训练完成 {task_id}:{instrument} # {model_name}")

        # 3. 构建回测 executor
        executor = SimulatorExecutor(
            time_per_step="day",
            start_time=start_time,
            end_time=end_time,
            generate_portfolio_metrics=True,
        )

        # 4. 回测
        strategy_name = "topk"
        port_metrics, _ = backtest(
            start_time=start_time,
            end_time=end_time,
            strategy=strategy_name,
            executor=executor,
            benchmark="SH000300",
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
