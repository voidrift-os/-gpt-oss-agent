import pandas as pd
import pandas_ta as ta


def generate_signal(df: pd.DataFrame, rsi_period=14, rsi_buy=30, rsi_sell=70):
    df = df.copy()
    df["rsi"] = ta.rsi(df["close"], length=rsi_period)
    last = df.iloc[-1]
    if last["rsi"] <= rsi_buy:
        return "buy"
    if last["rsi"] >= rsi_sell:
        return "sell"
    return "hold"
