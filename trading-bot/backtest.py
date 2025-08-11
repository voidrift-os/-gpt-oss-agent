import os, yaml, numpy as np, pandas as pd
from dotenv import load_dotenv
from core.exchange import Exchange
from strategies.sma_cross import generate_signal as sma_signal
from strategies.rsi_reversion import generate_signal as rsi_signal


def run_backtest(cfg):
    ex = Exchange(paper=True)
    df = ex.fetch_ohlcv_df(cfg["pair"], timeframe=cfg["timeframe"], limit=1000)

    cash = cfg["starting_balance"]
    pos = 0.0
    fee = cfg["fee_rate"]
    max_pct = cfg["max_position_pct"]

    def decide(d):
        name = cfg["strategy"]["name"]
        p = cfg["strategy"]["params"]
        if name == "sma_cross":
            return sma_signal(d, fast=p.get("fast", 20), slow=p.get("slow", 50))
        else:
            return rsi_signal(
                d,
                rsi_period=p.get("rsi_period", 14),
                rsi_buy=p.get("rsi_buy", 30),
                rsi_sell=p.get("rsi_sell", 70),
            )

    equity_curve = []
    for i in range(60, len(df)):
        window = df.iloc[:i].copy()
        price = window["close"].iloc[-1]
        signal = decide(window)

        # mark-to-market
        equity = cash + pos * price
        equity_curve.append(equity)

        # size rule
        max_units = (equity * max_pct) / price

        if signal == "buy" and pos < max_units:
            # buy up to max units
            buy_qty = max_units - pos
            cost = buy_qty * price
            trade_fee = cost * fee
            if cost + trade_fee <= cash:
                cash -= (cost + trade_fee)
                pos += buy_qty

        elif signal == "sell" and pos > 0:
            # sell all
            revenue = pos * price
            trade_fee = revenue * fee
            cash += (revenue - trade_fee)
            pos = 0.0

    final_price = df["close"].iloc[-1]
    final_equity = cash + pos * final_price
    ret = (final_equity / cfg["starting_balance"]) - 1
    print(f"Backtest on {cfg['pair']} ({cfg['timeframe']}):")
    print(f"Start: {cfg['starting_balance']:.2f}  End: {final_equity:.2f}  Return: {ret*100:.2f}%")


if __name__ == "__main__":
    load_dotenv()
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    run_backtest(cfg)
