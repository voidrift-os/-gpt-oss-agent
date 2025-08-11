import pandas as pd
import pandas_ta as ta


def generate_signal(df: pd.DataFrame, fast=20, slow=50):
    """Return last signal: 'buy', 'sell', or 'hold'."""
    df = df.copy()
    df["fast"] = df["close"].rolling(fast).mean()
    df["slow"] = df["close"].rolling(slow).mean()
    df["signal"] = 0
    df.loc[df["fast"] > df["slow"], "signal"] = 1
    df.loc[df["fast"] < df["slow"], "signal"] = -1
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if prev["signal"] <= 0 and last["signal"] > 0:
        return "buy"
    if prev["signal"] >= 0 and last["signal"] < 0:
        return "sell"
    return "hold"
