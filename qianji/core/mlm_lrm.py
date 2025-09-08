'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-07 19:28:25
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-08 09:50:39
FilePath: /miaosuan/qianji/core/mlm_lrm.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import pandas as pd
from sklearn.linear_model import LinearRegression


from .ml_model import MLModel

class LinearRegressionModel(MLModel):
    def train(self, df: pd.DataFrame):
        df["$close_shift1"] = df["$close"].groupby("instrument").shift(1)
        df["$volume_shift1"] = df["$volume"].groupby("instrument").shift(1)
        df = df.dropna()

        X = df[["$close_shift1", "$volume_shift1"]]
        y = df["$close"]

        self.df_train = df
        self.model = LinearRegression()
        self.model.fit(X, y)

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")

        df["$close_shift1"] = df["$close"].groupby("instrument").shift(1)
        df["$volume_shift1"] = df["$volume"].groupby("instrument").shift(1)
        df = df.dropna()

        X = df[["$close_shift1", "$volume_shift1"]]
        pred = self.model.predict(X)
        pred_df = df.reset_index()[["datetime", "instrument"]].copy()
        pred_df["score"] = pred
        return pred_df
