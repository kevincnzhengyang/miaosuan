'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-07 19:29:35
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-08 09:50:44
FilePath: /miaosuan/qianji/core/mlm_lgbm.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import pandas as pd
import lightgbm as lgb

from .ml_model import MLModel

class LightGBMModel(MLModel):
    def train(self, df: pd.DataFrame):
        df["$close_shift1"] = df["$close"].groupby("instrument").shift(1)
        df["$volume_shift1"] = df["$volume"].groupby("instrument").shift(1)
        df = df.dropna()

        X = df[["$close_shift1", "$volume_shift1"]]
        y = df["$close"]

        self.df_train = df
        self.model = lgb.LGBMRegressor(
            n_estimators=200,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )
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
