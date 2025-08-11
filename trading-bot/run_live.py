import os, time, yaml
from dotenv import load_dotenv
from core.exchange import Exchange
from core.risk import cap_position
from core.notifier import notify
from strategies.sma_cross import generate_signal as sma_signal
from strategies.rsi_reversion import generate_signal as rsi_signal

load_dotenv()

def pick_strategy(name):
    return sma_signal if name == "sma_cross" else rsi_signal


if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    ex_id = os.getenv("EXCHANGE", "binance")
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    ex = Exchange(
        exchange_id=ex_id,
        api_key=api_key,
        api_secret=api_secret,
        paper=cfg["paper_trading"],
        starting_balance=cfg["starting_balance"],
        fee_rate=cfg["fee_rate"],
    )

    decide = pick_strategy(cfg["strategy"]["name"])
    pair = cfg["pair"]
    tf = cfg["timeframe"]

    notify(f"▶️ Bot started: {pair} {tf} | paper={cfg['paper_trading']}")
    while True:
        df = ex.fetch_ohlcv_df(pair, timeframe=tf, limit=500)
        price = df["close"].iloc[-1]
        signal = decide(df, **cfg["strategy"]["params"])

        # Position sizing: cap by % of equity (paper broker tracks internally)
        if ex.paper:
            equity = ex.broker.mark_to_market(price)
            max_units = cap_position(equity, price, cfg["max_position_pct"])
            current_units = ex.broker.position
        else:
            max_units = None
            current_units = 0  # (for brevity; real mode would query positions)

        if signal == "buy":
            qty = max(0.0, (max_units or 0) - current_units)
            if qty > 0:
                ok, msg = ex.market_buy(pair, qty, price_hint=price)
                if ok:
                    notify(
                        f"✅ {msg} | equity≈{ex.equity(price, pair) if ex.paper else 'n/a'}"
                    )
        elif signal == "sell":
            qty = current_units
            if qty > 0:
                ok, msg = ex.market_sell(pair, qty, price_hint=price)
                if ok:
                    notify(
                        f"✅ {msg} | equity≈{ex.equity(price, pair) if ex.paper else 'n/a'}"
                    )

        time.sleep(cfg["poll_seconds"])
