import numpy as np
import pandas as pd


def bollinger(df: pd.DataFrame, window: int = 20):
    df["Support"] = df["Low"].rolling(window=window, center=True).min()
    df["Resistance"] = df["High"].rolling(window=window, center=True).max()

def sma(df: pd.DataFrame, num_periods: int):
    col_name = f"SMA{num_periods}"
    df[col_name] = df["Close"].rolling(window=num_periods).mean()