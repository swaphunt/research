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

## License

The price data in this study comes from Binance Vision, which is licensed CC BY-NC-SA 4.0. Everything derived from it is therefore licensed **CC BY-NC-SA 4.0** (https://creativecommons.org/licenses/by-nc-sa/4.0/), not CC BY 4.0: the files in `data/results/`, the charts in `charts/` and the figures in `FINDINGS.md`. Non-commercial use only; share adaptations under the same licence. Credit: "SwapHunt (swaphunt.dev). Price data: Binance Vision". Code: MIT.

## Versions

- `extreme-fear-v1` (2026-10-31): first publication.
- `extreme-fear-v2` (2026-11-01): adds the credit "Price data: Binance Vision" to the method notes and every chart, and licenses everything derived from the Binance price data CC BY-NC-SA 4.0 (see License). The numbers are unchanged.
