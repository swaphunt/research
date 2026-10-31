# extreme-fear

- **Status:** published
- **Data period:** 2018-02-01 – 2026-10-28
- **Published:** 2026-10-31, [https://swaphunt.dev/research/extreme-fear-bitcoin-buy-signal](https://swaphunt.dev/research/extreme-fear-bitcoin-buy-signal)

## Run

```
python -m venv venv && venv/bin/pip install -r requirements.txt
./run_all.sh
```

`run_all.sh` runs all scripts in order and finally `shared/check_numbers.py` against `article.md` (if present) and `FINDINGS.md`.

| Script | What |
|---|---|
| `00_extract.py` | Fetches Fear & Greed (alternative.me) and BTCUSDT daily candles (Binance) as raw responses to `data/raw/`. Uses existing raw data; `--refresh` fetches again |
| `01_prepare.py` | Daily table `data/results/private/daily.csv` (index values and BTC prices; not redistributed), data quality and zone/episode counts in `findings.json` |
| `02_analysis.py` | Forward returns after episodes against all days, random days and a matched baseline; bootstrap, robustness and leave-one-year-out |
| `03_charts.py` | Three charts (PNG + SVG) for the article using `shared/chartstyle.py` |
| `04_tables.py` | The episode table for the article (`data/results/episodes_table.md`), generated from findings.json |

## Folders
- `scripts/`: numbered scripts
- `data/raw/`: created locally by `00_extract.py`; raw responses are not redistributed, see `data/SOURCES.md`
- `data/results/findings.json`: all key figures; `allowed_numbers.json`: constants and the brief's figures
- `charts/`: PNG and SVG
- `FINDINGS.md`: key figures, definitions and caveats
- Article: https://swaphunt.dev/research/extreme-fear-bitcoin-buy-signal
