'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-07 19:22:50
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-08 09:50:41
FilePath: /miaosuan/qianji/core/factory.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
from .ml_model import MLModel
from .mlm_lrm import LinearRegressionModel
from .mlm_lgbm import LightGBMModel
from .mlm_xgbm import XGBoostModel

class ModelFactory:
    models = {
        "linear_regression": LinearRegressionModel,
        "xgboost": XGBoostModel,
        "lightgbm": LightGBMModel,
    }

    @staticmethod
    def get_model(name: str) -> MLModel:
        if name not in ModelFactory.models:
            raise ValueError(f"Unknown model: {name}")
        return ModelFactory.models[name]()

