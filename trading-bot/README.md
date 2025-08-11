# Trading Bot (Paper + Live)

- Two strategies: `sma_cross`, `rsi_reversion`
- Paper trading by default; flip `paper_trading: false` + add `API_KEY`, `API_SECRET` for live
- Telegram alerts supported (optional)

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # add keys if going live
python backtest.py
python run_live.py
```

## Notes

- Start with paper mode. Do NOT sell this as guaranteed profits.
- For live mode, use small size, add stop-loss logic, and test thoroughly.
