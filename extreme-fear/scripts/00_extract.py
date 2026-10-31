"""Fetch Fear & Greed history (alternative.me) and daily BTC prices (Binance) as raw responses.

Output: data/raw/fng.json, data/raw/btc_klines_*.json and data/raw/fetch_log.json
(url, time, HTTP status, sha256 per file). Runs politely with an identifiable User-Agent.

If raw data already exists, it is used (so the study can be reproduced exactly). `--refresh` fetches again.
"""
import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

import common as C

UA = "SwapHuntResearchBot/1.0 (+https://swaphunt.dev/about)"
FNG_URL = "https://api.alternative.me/fng/?limit=0&format=json"
# api.binance.com is not reachable from here; data-api.binance.vision is Binance's public market data mirror
KLINES_URL = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1000&startTime={start}"
BTC_START_MS = 1501545600000  # 2017-08-01, before the first BTCUSDT day (2017-08-17)


def fetch(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read()


def save(name: str, url: str, status: int, body: bytes, log: list):
    (C.RAW / name).write_bytes(body)
    log.append({"file": name, "url": url, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "http_status": status, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)})


def main():
    C.RAW.mkdir(parents=True, exist_ok=True)
    if (C.RAW / "fetch_log.json").exists() and "--refresh" not in sys.argv:
        print("raw data exists (data/raw/fetch_log.json); use --refresh to fetch again")
        return
    log = []
    status, body = fetch(FNG_URL)
    save("fng.json", FNG_URL, status, body, log)

    start, page = BTC_START_MS, 0
    while True:
        time.sleep(1)
        url = KLINES_URL.format(start=start)
        status, body = fetch(url)
        rows = json.loads(body)
        if not rows:
            break
        page += 1
        save(f"btc_klines_{page:02d}.json", url, status, body, log)
        start = rows[-1][0] + 86_400_000  # next day's open_time
        if len(rows) < 1000:
            break

    (C.RAW / "fetch_log.json").write_text(json.dumps(log, indent=2) + "\n")
    for e in log:
        print(f"{e['file']}: HTTP {e['http_status']}, {e['bytes']} bytes")


if __name__ == "__main__":
    main()
