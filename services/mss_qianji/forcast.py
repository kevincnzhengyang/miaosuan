'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-11-11 15:09:46
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-11-13 12:47:21
FilePath: /miaosuan/services/mss_qianji/forcast.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import numpy as np
import pandas as pd

from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

# SARIMAX 方法
def _sarimax_forecast(series, n_forecast=5, order=(1,1,1)):
    # 补充频率信息
    if series.index.freq is None:
        try:
            series = series.asfreq('B')  # 工作日
        except ValueError:
            series = series.asfreq('D')  # 普通日
            
    model = SARIMAX(series, order=order, enforce_stationarity=False, enforce_invertibility=False)
    res = model.fit(disp=False)
    pred = res.get_forecast(steps=n_forecast) # type: ignore
    mean = pred.predicted_mean
    ci = pred.conf_int(alpha=0.05)
    lower = ci.iloc[:, 0]
    upper = ci.iloc[:, 1]
    idx = pd.bdate_range(series.index[-1] + pd.Timedelta(days=1), periods=n_forecast)
    return pd.Series(mean.values, idx), pd.Series(lower.values, idx), pd.Series(upper.values, idx)

# GBM 模拟方法
def _gbm_simulate(series, n_forecast=5, n_sim=5000):
    logret = np.log(series / series.shift(1)).dropna()
    mu, sigma = logret.mean(), logret.std()
    S0 = series.iloc[-1]
    rng = np.random.default_rng(42)
    sims = np.zeros((n_sim, n_forecast))
    for i in range(n_sim):
        eps = rng.standard_normal(n_forecast)
        path = np.zeros(n_forecast)
        S_t = S0
        for t in range(n_forecast):
            S_t = S_t * np.exp((mu - 0.5 * sigma**2) + sigma * eps[t])
            path[t] = S_t
        sims[i] = path
    # 用路径方差反映不确定性增长
    # lower = np.quantile(sims, 0.05, axis=0)
    # upper = np.quantile(sims, 0.95, axis=0)
    median = np.median(sims, axis=0)
    path_std = np.std(sims, axis=0)
    upper = median + 1.65 * path_std
    lower = median - 1.65 * path_std
    idx = pd.bdate_range(series.index[-1] + pd.Timedelta(days=1), periods=n_forecast)
    return pd.Series(median, idx), pd.Series(lower, idx), pd.Series(upper, idx)

def _make_features(series, lags=[1,2,3,5,10]):
    df_feat = pd.DataFrame({'y': series})
    for lag in lags:
        df_feat[f'lag_{lag}'] = df_feat['y'].shift(lag)
    df_feat['ma5'] = df_feat['y'].rolling(5).mean()
    df_feat['ma10'] = df_feat['y'].rolling(10).mean()
    df_feat = df_feat.dropna()
    return df_feat

# Quantile Regression 方法
def _quantile_regression_forecast(series, n_forecast=5):
    df_feat = _make_features(series)
    X = df_feat.drop(columns=['y'])
    y = df_feat['y']
    sc = StandardScaler()
    Xs = sc.fit_transform(X)
    # 改为递推预测
    X_train = Xs
    y_train = y.to_numpy(dtype=float)
    models = {a: GradientBoostingRegressor(loss='quantile', alpha=a, n_estimators=200, max_depth=3)
              for a in [0.05, 0.5, 0.95]}
    for m in models.values():
        m.fit(X_train, y_train)
    last_row = df_feat.iloc[-1:].copy()
    preds = {a: [] for a in models}
    for i in range(n_forecast):
        feat = _make_features(pd.concat([series, last_row['y']]))
        Xf = sc.transform(feat.drop(columns=['y']).iloc[[-1]])
        for a, m in models.items():
            y_pred = m.predict(Xf)[0]
            preds[a].append(y_pred)
        # 滚动加入新预测
        new_y = pd.Series([preds[0.5][-1]], index=[series.index[-1] + pd.Timedelta(days=i+1)])
        series = pd.concat([series, new_y])
    idx = pd.bdate_range(series.index[-n_forecast], periods=n_forecast)
    return pd.Series(preds[0.5], idx), pd.Series(preds[0.05], idx), pd.Series(preds[0.95], idx)
    # 本质是历史重放，废止
    # X_pred = Xs[-n_forecast:]
    # def _fit(alpha):
    #     model = GradientBoostingRegressor(loss='quantile', alpha=alpha, n_estimators=200, max_depth=3)
    #     model.fit(Xs[:-n_forecast], y[:-n_forecast])
    #     return model.predict(X_pred)
    # q05 = _fit(0.05)
    # q50 = _fit(0.5)
    # q95 = _fit(0.95)
    # idx = pd.bdate_range(series.index[-1] + pd.Timedelta(days=1), periods=n_forecast)
    # return pd.Series(q50, idx), pd.Series(q05, idx), pd.Series(q95, idx)

# 集成预测方法
def _ensemble_forecast(*methods):
    all_means, all_lows, all_ups = zip(*methods)
    idx = all_means[0].index
    df = pd.DataFrame(index=idx)
    df['point'] = np.mean(np.column_stack([m.values for m in all_means]), axis=1)
    # 改为“分布平均”，而不是“交集”
    # df['lower'] = np.max(np.column_stack([l.values for l in all_lows]), axis=1)
    # df['upper'] = np.min(np.column_stack([u.values for u in all_ups]), axis=1)
    df['lower'] = np.mean(np.column_stack([l.values for l in all_lows]), axis=1)
    df['upper'] = np.mean(np.column_stack([u.values for u in all_ups]), axis=1)
    return df

def forecast_next_week(df, n_forecast=5):
    if 'close' not in df.columns:
        raise ValueError("DataFrame must contain 'close' column")
    series = df['close'].dropna()
    sarimax_m, sarimax_l, sarimax_u = _sarimax_forecast(series, n_forecast)
    gbm_m, gbm_l, gbm_u = _gbm_simulate(series, n_forecast)
    gbr_m, gbr_l, gbr_u = _quantile_regression_forecast(series, n_forecast)
    forecast_df = _ensemble_forecast((sarimax_m, sarimax_l, sarimax_u),
                                     (gbm_m, gbm_l, gbm_u),
                                     (gbr_m, gbr_l, gbr_u))
    return forecast_df
