import os, ccxt, time
import pandas as pd


class PaperBroker:
    def __init__(self, starting_balance=1000.0, fee_rate=0.0004):
        self.balance = starting_balance
        self.position = 0.0
        self.avg_price = 0.0
        self.fee_rate = fee_rate
        self.equity = starting_balance

    def _apply_fee(self, usd_value):
        return usd_value * self.fee_rate

    def buy(self, price, qty):
        cost = price * qty
        fee = self._apply_fee(cost)
        if cost + fee > self.balance:
            return False, "Insufficient balance"
        # update position
        new_total = self.position + qty
        self.avg_price = (self.avg_price * self.position + price * qty) / max(new_total, 1e-9)
        self.position = new_total
        self.balance -= (cost + fee)
        return True, f"BUY {qty:.6f} @ {price:.2f} (fee {fee:.2f})"

    def sell(self, price, qty):
        qty = min(qty, self.position)
        if qty <= 0:
            return False, "No position to sell"
        revenue = price * qty
        fee = self._apply_fee(revenue)
        self.position -= qty
        self.balance += (revenue - fee)
        if self.position == 0:
            self.avg_price = 0.0
        return True, f"SELL {qty:.6f} @ {price:.2f} (fee {fee:.2f})"

    def mark_to_market(self, price):
        pos_value = self.position * price
        self.equity = self.balance + pos_value
        return self.equity


class Exchange:
    """Thin wrapper around ccxt for candles + orders. Defaults to paper mode."""

    def __init__(
        self,
        exchange_id="binance",
        api_key=None,
        api_secret=None,
        paper=True,
        starting_balance=1000.0,
        fee_rate=0.0004,
    ):
        self.paper = paper
        if paper:
            self.broker = PaperBroker(starting_balance, fee_rate)
            self.client = None
        else:
            ex_cls = getattr(ccxt, exchange_id)
            self.client = ex_cls(
                {
                    "apiKey": api_key or "",
                    "secret": api_secret or "",
                    "enableRateLimit": True,
                }
            )
            self.client.load_markets()

    def fetch_ohlcv_df(self, symbol, timeframe="5m", limit=500):
        if self.paper:
            # For paper mode we still fetch from ccxt public endpoints
            client = ccxt.binance({"enableRateLimit": True})
            ohlcv = client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        else:
            ohlcv = self.client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "volume"])
        df["ts"] = pd.to_datetime(df["ts"], unit="ms")
        return df

    def last_price(self, symbol):
        if self.paper:
            client = ccxt.binance({"enableRateLimit": True})
            return client.fetch_ticker(symbol)["last"]
        else:
            return self.client.fetch_ticker(symbol)["last"]

    def market_buy(self, symbol, qty, price_hint=None):
        if self.paper:
            price = price_hint or self.last_price(symbol)
            return self.broker.buy(price, qty)
        else:
            o = self.client.create_market_buy_order(symbol, qty)
            return True, str(o)

    def market_sell(self, symbol, qty, price_hint=None):
        if self.paper:
            price = price_hint or self.last_price(symbol)
            return self.broker.sell(price, qty)
        else:
            o = self.client.create_market_sell_order(symbol, qty)
            return True, str(o)

    def equity(self, price_hint=None, symbol=None):
        if self.paper and price_hint and symbol:
            return self.broker.mark_to_market(price_hint)
        return None
