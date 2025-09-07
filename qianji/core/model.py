import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np

class MLModel:
    def __init__(self, model_type='lgb'):
        if model_type=='lgb':
            self.model = LGBMRegressor()
        else:
            raise NotImplementedError
        self.scaler = StandardScaler()

    def train(self, X: pd.DataFrame, y: pd.Series):
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict(self, X: pd.DataFrame):
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def generate_signal(self, pred: pd.Series, threshold=0.01):
        signal = np.where(pred>threshold, 1, np.where(pred<-threshold,-1,0))
        return signal
