import time
from datetime import datetime

def now_ts():
    return int(time.time())

def ts_to_str(ts):
    return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
