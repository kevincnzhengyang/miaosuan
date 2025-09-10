import abc
import pandas as pd

class MLModel(abc.ABC):
    """抽象基类，定义模型训练、预测、信号生成、指标计算"""

    def __init__(self):
        self.model = None

    @abc.abstractmethod
    def train(self, df: pd.DataFrame):
        """训练模型"""
        pass

    @abc.abstractmethod
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """返回 DataFrame，列: datetime, instrument, score"""
        pass

    def generate_signal(self, df: pd.DataFrame, pred: pd.Series) -> pd.DataFrame:
        """把预测结果转为 QLib 回测需要的格式"""
        pred_df = df.reset_index()[["datetime", "instrument"]].copy()
        pred_df["score"] = pred
        return pred_df
