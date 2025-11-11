'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-10-31 21:17:00
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-11-11 10:38:09
FilePath: /miaosuan/services/mss_qianji/ta_hly.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from loguru import logger
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from plotly.subplots import make_subplots

from config.settings import settings
from helper.telegram_bot import telegram_broadcast_image, telegram_broadcast_report


# 准备技术指标数据
def _prepare_ta_hly(symbol: str, span: int = 100) -> pd.DataFrame:
    # 读取CSV数据
    df = pd.read_csv(f"{settings.DATA_DIR}/csv/{symbol}.csv").tail(span)
    df = df[['date', 'open', 'high', 'low', 'close', 'volume', 
        'HLY_GRAV', 'HLY_ATT_UPPER', 'HLY_ATT_LOWER', 
        'HLY_ESC_UPPER', 'HLY_ESC_LOWER', 'HLY_VMA5_II',
        'VMA5', 'ATR14', 'VOSL']]
    if df is None or len(df) == 0:
        logger.error(f"技术指标数据为空: {symbol}")
        return pd.DataFrame()
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')

    # ----------------------------------
    #           计算各衍生指标
    # ----------------------------------
    # hvp 高价格波动率，高于ATR14的第三四分位数
    df['hvp'] = df['ATR14'] > df['ATR14'].rolling(5).quantile(0.75)
    # lvp 低价格波动率，低于ATR14的第一四分位数
    df['lvp'] = df['ATR14'] < df['ATR14'].rolling(5).quantile(0.25)
    # vpi 价格波动率放大
    df['vpi'] = df['ATR14'].diff().ewm(span=10, adjust=False).mean() > 0

    # 成交量指标
    df['hly_mark'] = df['volume'] >= df['HLY_VMA5_II']
    df['vslope'] = df['VOSL'].diff()

    #  值     状态	                含义	        策略意义
    #  2     volume_rising	    成交量快速放大	    趋势确认信号
    # -1    volume_peaking	    成交量高位回落	    警惕顶部
    #  1    volume_recovering	成交量从低位恢复    可能启动趋势
    #  0    volume_weak	        成交量持续低迷	    震荡或衰退期
    df['vstate'] = np.select(
        [
            (df['VOSL'] > 0) & (df['vslope'] > 0),
            (df['VOSL'] > 0) & (df['vslope'] < 0),
            (df['VOSL'] < 0) & (df['vslope'] > 0)
        ],
        [2, -1, 1],
        default=0
    )

    # 地心引力线的趋势
    df['hly_trend'] = np.select(
        [
            df['HLY_GRAV'].diff(5) > 0,  # type: ignore
            df['HLY_GRAV'].diff(5) < 0   # type: ignore
        ],
        [1, -1],
        default=0
    )

    # 连续10天高于引力线上限
    df['hly_att_above'] = df['high'] > df['HLY_ATT_UPPER']
    df['hly_att_above_10d'] = df['hly_att_above'].rolling(window=10).sum() == 10
    # 连续 True 分组
    df['group_above'] = (df['hly_att_above'] != df['hly_att_above'].shift()).cumsum()
    # 每段连续计数（累计长度）
    df['streak_above'] = df.groupby('group_above')['hly_att_above'].transform(lambda x: x.cumsum() if x.iloc[0] else 0)
    # 标记第一天
    df['hly_att_above_10d_start'] = (
        (df['streak_above'] == 1) &                                   # 每段的第一天
        (df.groupby('group_above')['streak_above'].transform('max') >= 10)   # 该段长度 ≥ 10
    )

    # 连续10天小于引力线下限
    df['hly_att_blow'] = df['low'] < df['HLY_ATT_LOWER']
    df['hly_att_blow_10d'] = df['hly_att_blow'].rolling(window=10).sum() == 10
    # 连续 True 分组
    df['group_below'] = (df['hly_att_blow'] != df['hly_att_blow'].shift()).cumsum()
    # 每段连续计数（累计长度）
    df['streak_below'] = df.groupby('group_below')['hly_att_blow'].transform(lambda x: x.cumsum() if x.iloc[0] else 0)
    # 标记第一天
    df['hly_att_blow_10d_start'] = (
        (df['streak_below'] == 1) &                                   # 每段的第一天
        (df.groupby('group_below')['streak_below'].transform('max') >= 10)   # 该段长度 ≥ 10
    )

    # 标记价格区间
    df['hly_state'] = np.select(
        [
            df['close'] <= df['HLY_ESC_LOWER'],
            (df['close'] > df['HLY_ESC_LOWER']) & (df['close'] <= df['HLY_ATT_LOWER']),
            (df['close'] > df['HLY_ATT_LOWER']) & (df['close'] <= df['HLY_GRAV']),
            (df['close'] > df['HLY_GRAV']) & (df['close'] <= df['HLY_ATT_UPPER']),
            (df['close'] > df['HLY_ATT_UPPER']) & (df['close'] <= df['HLY_ESC_UPPER']),
            (df['close'] > df['HLY_ESC_UPPER'])
        ],
        [-3, -2, -1, 1, 2, 3],
        default=0
    )

    # 删除中间结果
    df = df.drop(columns=['vslope', 'hly_att_above', 'group_above', 'streak_above', 
                        'hly_att_blow', 'group_below', 'streak_below'])
    

    # ----------------------------------
    #           日周共振
    # ----------------------------------
    # 日线与周线多周期共振
    df_daily = pd.read_csv(f"{settings.DATA_DIR}/csv/{symbol}.csv").tail(span+500)
    df_daily = df_daily[['date', 'open', 'high', 'low', 'close', 'volume']]
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_daily = df_daily.set_index('date')
    # 计算周线
    df_weekly = df_daily.resample('W').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })

    # 计算周线的胡立阳地心引力线指标.
    df_weekly['HLY_GRAV'] = (df_weekly['close'].rolling(30).mean() + df_weekly['close'].rolling(72).mean()) / 2
    df_weekly['HLY_ATT_UPPER'] = df_weekly['HLY_GRAV'] * 1.1
    df_weekly['HLY_ATT_LOWER'] = df_weekly['HLY_GRAV'] * 0.9
    df_weekly['HLY_ESC_UPPER'] = df_weekly['HLY_GRAV'] * 1.2
    df_weekly['HLY_ESC_LOWER'] = df_weekly['HLY_GRAV'] * 0.8
    df_weekly['HLY_VMA5_II'] = df_weekly['volume'].rolling(2).mean() * 2

    # 地心引力线的趋势
    df_weekly['hly_trend'] = np.select(
        [
            df_weekly['HLY_GRAV'].diff(5) > 0,  # type: ignore
            df_weekly['HLY_GRAV'].diff(5) < 0   # type: ignore
        ],
        [1, -1],
        default=0
    )

    # 标记价格区间
    df_weekly['hly_state'] = np.select(
        [
            df_weekly['close'] <= df_weekly['HLY_ESC_LOWER'],
            (df_weekly['close'] > df_weekly['HLY_ESC_LOWER']) & (df_weekly['close'] <= df_weekly['HLY_ATT_LOWER']),
            (df_weekly['close'] > df_weekly['HLY_ATT_LOWER']) & (df_weekly['close'] <= df_weekly['HLY_GRAV']),
            (df_weekly['close'] > df_weekly['HLY_GRAV']) & (df_weekly['close'] <= df_weekly['HLY_ATT_UPPER']),
            (df_weekly['close'] > df_weekly['HLY_ATT_UPPER']) & (df_weekly['close'] <= df_weekly['HLY_ESC_UPPER']),
            (df_weekly['close'] > df_weekly['HLY_ESC_UPPER'])
        ],
        [-3, -2, -1, 1, 2, 3],
        default=0
    )

    # 对其日线与周线数据
    df['wk_HLY_GRAV'] = df_weekly['HLY_GRAV'].reindex(df.index, method='ffill')
    df['wk_HLY_ATT_UPPER'] = df_weekly['HLY_ATT_UPPER'].reindex(df.index, method='ffill')
    df['wk_HLY_ATT_LOWER'] = df_weekly['HLY_ATT_LOWER'].reindex(df.index, method='ffill')
    df['wk_HLY_ESC_UPPER'] = df_weekly['HLY_ESC_UPPER'].reindex(df.index, method='ffill')
    df['wk_HLY_ESC_LOWER'] = df_weekly['HLY_ESC_LOWER'].reindex(df.index, method='ffill')
    df['wk_HLY_VMA5_II'] = df_weekly['HLY_VMA5_II'].reindex(df.index, method='ffill')
    df['wk_hly_trend'] = df_weekly['hly_trend'].reindex(df.index, method='ffill')
    df['wk_hly_state'] = df_weekly['hly_state'].reindex(df.index, method='ffill')

    # 判断日周共振
    df['d_w_r_trend'] = df['wk_hly_trend'] == df['hly_trend']
    return df

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

def _forecast_next_week(df, n_forecast=5):
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

def _plot_ta_hly(df: pd.DataFrame, symbol: str, forecast_df: pd.DataFrame) -> go.Figure:
    df['date'] = df.index.strftime("%Y-%m-%d")  # type: ignore

    # 创建子图
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05,
        subplot_titles=(f"{symbol} - 每日技术分析 - 胡立阳地心引力线", "")
    )

    # ---------- 蜡烛图 ----------
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        increasing_line_color='red',       # 涨时线条颜色
        increasing_fillcolor='red',        # 涨时填充颜色
        decreasing_line_color='green',     # 跌时线条颜色
        decreasing_fillcolor='green',      # 跌时填充颜色
        name="Quote", 
        showlegend=False
    ), row=1, col=1)

    # ---------- Gravity & 边界 ----------
    fig.add_trace(go.Scatter(
        x=df['date'], y=df["HLY_GRAV"],
        mode="lines", name="Daily_G", line=dict(color="blue", width=2), 
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['date'], y=df["HLY_ATT_UPPER"],
        mode="lines", name="Attr_Upper", line=dict(color="orange", dash="dash"), 
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['date'], y=df["HLY_ATT_LOWER"],
        mode="lines", name="Att_Lower", line=dict(color="brown", dash="dash"), 
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['date'], y=df["HLY_ESC_UPPER"],
        mode="lines", name="Esc_Upper", line=dict(color="red", dash="dot"), 
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['date'], y=df["HLY_ESC_LOWER"],
        mode="lines", name="Esc_Lower", line=dict(color="purple", dash="dot"), 
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['date'], y=df["wk_HLY_GRAV"],
        mode="lines", name="Weekly_Gravity", line=dict(color="navy", width=3, dash="dot"), 
        showlegend=False
    ), row=1, col=1)

    # ---------- 突破信号 ----------
    up_points = df[df["hly_att_above_10d_start"]]
    down_points = df[df["hly_att_blow_10d_start"]]
    mark_points = df[df["hly_mark"]]

    fig.add_trace(go.Scatter(
        x=up_points["date"], y=up_points["HLY_GRAV"]*0.95,
        mode="markers", name="Up Break",
        marker=dict(symbol="triangle-up", size=12, color="red"), 
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=down_points["date"], y=down_points["HLY_GRAV"]*1.05,
        mode="markers", name="Down Break",
        marker=dict(symbol="triangle-down", size=12, color="green"), 
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=mark_points["date"], y=mark_points["HLY_ESC_LOWER"]*0.95,
        mode="markers", name="Vol Mark",
        marker=dict(symbol="star", size=12, color="black"), 
        showlegend=False
    ), row=1, col=1)

    # ---------- 成交量 + vma5 ----------
    colors = ["red" if row["close"] >= row["open"] else "green" for _, row in df.iterrows()]
    fig.add_trace(go.Bar(
        x=df['date'], y=df["volume"],
        marker_color=colors, name="Vol", 
        showlegend=False
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df['date'], y=df["VMA5"],
        mode="lines", name="VMA5", line=dict(color="blue", width=1.5), 
        showlegend=False
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df['date'], y=df["HLY_VMA5_II"],
        mode="lines", name="VMA5*2", line=dict(color="orange", width=2), 
        showlegend=False
    ), row=2, col=1)

    # 预测点
    # 预测区间 (上下置信区间)
    # 上界
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['upper'],
        mode='lines',
        line=dict(width=0),
        name='上界', 
        showlegend=False
    ))

    # 下界 + 填充
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['lower'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(255,165,0,0.2)',
        line=dict(width=0),
        name='预测区间', 
        showlegend=False
    ))

    # 中值线
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['point'],
        mode='lines+markers',
        name='预测中值', 
        showlegend=False,
        line=dict(color='orange', width=2, dash='dot'),
        text=[f"{v:.2f}" for v in forecast_df['point']],
        textposition='top center',
        hovertemplate=(
            "日期: %{x|%Y-%m-%d}<br>"
            "中值: %{y:.2f}<br>"
            "上限: %{customdata[0]:.2f}<br>"
            "下限: %{customdata[1]:.2f}<extra></extra>"
        ),
        customdata=np.stack([forecast_df['upper'], forecast_df['lower']], axis=-1)
    ))

    # 只显示每月首个交易日，自动延伸一点X轴，去掉非交易日空白, 设置X轴日期格式与角度
    tickvals = df.groupby(pd.Grouper(freq='ME')).head(1)["date"]
    fig.update_xaxes(
        range=[df.index.min(), forecast_df.index.max() + pd.Timedelta(days=1)],
        type="category",
        tickvals=tickvals,
        tickformat="%Y-%m-%d",
        tickangle=45
    )

    # ---------- 布局美化 ----------
    fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=False)),
        yaxis_title="Price (HKD)",
        yaxis2_title="Volume",
        template="plotly_white",
        width=1200, height=800,
        hovermode="x unified",
        xaxis_autorange=True,
        yaxis_autorange=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1)
    )

    return fig

async def ta_hly_analysis(symbol: str, span: int = 100, n_forecast: int = 5):
    logger.debug(f"HLY分析: {symbol}")
    df = _prepare_ta_hly(symbol, span)
    if df is None or len(df) == 0:
        logger.error(f"无法准备技术指标数据: {symbol}")
        return
    forecast_df = _forecast_next_week(df, n_forecast)
    fig = _plot_ta_hly(df, symbol, forecast_df)

    img_path = f"{settings.LOG_DIR}/{symbol}_ta_hly.png"  # type: ignore
    fig.write_image(img_path, scale=2)
    caption = f"每日技术分析-HLY"
    await telegram_broadcast_image(img_path, caption)
    logger.info(f"HLY每日技术分析 {symbol}完成")

    # TODO: 发送文字报告
    # text = (
    #     f"* {msg.tag}\\=\\=\\={msg.name} *\n"
    #     f"🏷 股票: `{msg.symbol}`\n"
    #     f"🛎 开盘: `{msg.ohlc['open']}`\n"
    #     f"🔔 收盘: `{msg.ohlc['close']}`\n"
    #     f"🔼 最高: `{msg.ohlc['high']}`\n"
    #     f"🔽 最低: `{msg.ohlc['low']}`\n"
    #     f"💰 成交量: `{msg.ohlc['volume']}`\n"
    #     f"{arrow} 涨跌幅: `{msg.ohlc['pct_chg']:.2f}%`\n"
    #     f"🌊 振幅: `{msg.ohlc['pct_amp']:.2f}%`"
    # )
    # await telegram_broadcast_report(text)
