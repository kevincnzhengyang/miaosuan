import pandas as pd
import numpy as np

def alpha158(df: pd.DataFrame):
    """Alpha158 简化示例"""
    df = df.copy()
    df['alpha158'] = df['close'].pct_change() - df['open'].pct_change()
    return df[['datetime','alpha158']]

def alpha360(df: pd.DataFrame):
    """Alpha360 简化示例"""
    df = df.copy()
    df['alpha360'] = (df['high'] - df['low']) / df['close'].shift(1)
    return df[['datetime','alpha360']]
