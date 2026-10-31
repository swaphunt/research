# Data sources

| Source | What | Fetched | Script | Notes | Redistribution |
|---|---|---|---|---|---|
| alternative.me Fear & Greed API, `https://api.alternative.me/fng/?limit=0&format=json` | Daily index value (0-100) and label, 2018-02-01 onwards | 2026-10-29 | `00_extract.py` | No robots.txt (404). Timestamp 00:00 UTC per day. 4 days are missing. | redistribution: unclear. Only derived data (episodes, returns) and the fetch script are exported, not the index values |
| Binance market data, `https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d` | BTCUSDT daily candles (open time, OHLC, close time) from 2017-08-17 | 2026-10-29 | `00_extract.py` | Binance's public market data mirror; `api.binance.com` could not be reached. No robots.txt (404). The unfinished daily candle is left out in `01_prepare.py`. | redistribution: unclear. Only derived data and the fetch script are exported, not the prices |
| alternative.me, methodology page `https://alternative.me/crypto/fear-and-greed-index/` | The index's weights: volatility 25 %, momentum/volume 25 %, social media 15 %, surveys 15 % (paused), dominance 10 %, Google Trends 10 % | 2026-10-29 | private copy, not redistributed (sha256 5251e60c…696a) | Cited in the article's "Why it doesn't work" and in `allowed_numbers.json` (`source_alternative_me_method`). | redistribution: no. The copy stays private; the article links to the live page and a Wayback snapshot: https://web.archive.org/web/20261030201642/https://alternative.me/crypto/fear-and-greed-index/ (2026-10-30, weights checked) |

`00_extract.py` logs the URL, fetch time, HTTP status and sha256 for each raw file in `data/raw/fetch_log.json` when run locally; raw files are not redistributed.
