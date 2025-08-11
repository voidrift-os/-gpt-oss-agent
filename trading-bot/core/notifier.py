import os, requests

BOT = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT = os.getenv("TELEGRAM_CHAT_ID", "")

def notify(msg: str):
    if not BOT or not CHAT:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT}/sendMessage",
            data={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"},
            timeout=5
        )
    except Exception:
        pass
