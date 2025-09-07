import os
import pandas as pd
import qlib
from qlib.workflow import R
from core.factors import alpha158, alpha360
from core.model import MLModel
from core.backtest import backtest, calculate_metrics

qlib.init(provider_uri="~/.qlib/qlib_data/cn", region="cn")

class TaskWorkflowQLib:
    def __init__(self, task_id: str, df: pd.DataFrame):
        self.task_id = task_id
        self.df = df.copy()
        self.artifact_dir = os.path.join("artifacts", self.task_id)
        os.makedirs(self.artifact_dir, exist_ok=True)

    def run(self):
        # 启动实验
        with R.start(experiment_name=self.task_id) as r:
            recorder = R.get_recorder()

            # 1️⃣ 计算因子
            factor1 = alpha158(self.df)
            factor2 = alpha360(self.df)
            factors = pd.merge(factor1, factor2, on="datetime")

            # 保存因子
            factor_file = os.path.join(self.artifact_dir, "factors.parquet")
            factors.to_parquet(factor_file)
            recorder.log_artifact(factor_file, artifact_path="factors")

            # 2️⃣ 模型训练
            X = factors[['alpha158', 'alpha360']]
            y = self.df['close'].pct_change().fillna(0)

            model = MLModel()
            model.train(X, y)

            # 3️⃣ 生成信号
            # 直接生成 DataFrame 避免类型检查问题
            signals = pd.DataFrame({
                "datetime": factors['datetime'],
                "signal": pd.Series(model.generate_signal(pd.Series(model.predict(X))), index=factors.index),
                "price": self.df['close']
            })

            # 保存 signals
            signals_file = os.path.join(self.artifact_dir, "signals.parquet")
            signals.to_parquet(signals_file)
            recorder.log_artifact(signals_file, artifact_path="signals")

            # 4️⃣ 回测生成 equity
            equity_df = backtest(signals)
            equity_file = os.path.join(self.artifact_dir, "equity.parquet")
            equity_df.to_parquet(equity_file)
            recorder.log_artifact(equity_file, artifact_path="equity")

            # 5️⃣ 记录指标
            metrics = calculate_metrics(equity_df)
            recorder.log_metrics(**metrics)

            print(f"[{self.task_id}] 完成: metrics={metrics}")
            return metrics
