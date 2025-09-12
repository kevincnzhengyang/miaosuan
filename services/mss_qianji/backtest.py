import pandas as pd
import numpy as np

def backtest(df: pd.DataFrame, signal_col='signal', price_col='price', initial_cash=1_000_000):
    df = df.copy()
    df['position'] = df[signal_col].shift(1).fillna(0)
    df['returns'] = df[price_col].pct_change().fillna(0)
    df['equity'] = initial_cash * (1 + (df['position'] * df['returns']).cumsum())
    return df

def calculate_metrics(df: pd.DataFrame, equity_col='equity'):
    returns = df[equity_col].pct_change().fillna(0)
    annual_return = (1+returns.mean())**252 -1
    annual_vol = returns.std() * np.sqrt(252)
    sharpe = annual_return/annual_vol if annual_vol!=0 else 0
    max_drawdown = (df[equity_col]/df[equity_col].cummax() -1).min()
    return {
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown
    }
