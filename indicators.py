import numpy as np
import pandas as pd


def bollinger(df: pd.DataFrame, window: int = 20):
    df["bollingerLow"] = df["Low"].rolling(window=window, center=True).min()
    df["bollingerHigh"] = df["High"].rolling(window=window, center=True).max()

def sma(df: pd.DataFrame, num_periods: int):
    col_name = f"SMA{num_periods}"
    df[col_name] = df["Close"].rolling(window=num_periods).mean()

def is_far_from_level(df, l, levels):
    return np.sum([abs(l - x) < np.mean(df['High'] - df['Low']) for x in levels]) == 0

def add_support(df):
    """
    Adding support levels to the dataframe
    :return: List
    """
    levels = []

    def is_support(df, i):
        return df['Low'][i] < df['Low'][i - 1] and df['Low'][i] < df['Low'][i + 1] and df['Low'][i + 1] < df['Low'][i + 2] and df['Low'][i - 1] < df['Low'][i - 2]

    df['Support'] = np.nan
    
    for i in range(2, df.shape[0]-2):
        if is_support(df, i):
            l = df['Low'][i]
            if is_far_from_level(df, l, levels):
                levels.append((i, l))
                df.at[i, 'Support'] = l
    return levels

def add_resistance(df):
    """
    Adding resistance levels to the dataframe
    :return: List
    """
    levels = []

    def is_resistance(df, i):
        return df['High'][i] > df['High'][i - 1] and df['High'][i] > df['High'][i + 1] and df['High'][i + 1] > df['High'][i + 2] and df['High'][i - 1] > df['High'][i - 2]

    df['Resistance'] = np.nan

    for i in range(2, df.shape[0] - 2):
        if is_resistance(df, i):
            l = df['High'][i]
            if is_far_from_level(df, l, levels):
                levels.append((i, l))
                df.at[i, 'Resistance'] = l
    return levels