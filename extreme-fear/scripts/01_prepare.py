"""Combine Fear & Greed and BTC closing prices into one daily table and summarise the data basis.

Time alignment: the index value for day d has timestamp d 00:00 UTC and is known at the start of the day.
The entry price is the BTCUSDT close for the same UTC day d (Binance daily candle d 00:00-23:59 UTC),
so no information is used that was not known on the signal day.

Output: data/results/daily.csv, data/results/btc_daily.csv and data/ keys in findings.json.
"""
import json

import pandas as pd

import common as C

SRC = "scripts/01_prepare.py"


def load_fng() -> pd.DataFrame:
    d = json.loads((C.RAW / "fng.json").read_text())["data"]
    f = pd.DataFrame({
        "date": pd.to_datetime([int(x["timestamp"]) for x in d], unit="s", utc=True).date,
        "fng": [int(x["value"]) for x in d],
        "fng_label": [x["value_classification"] for x in d],
    })
    assert f.date.is_unique, "duplicates in Fear & Greed"
    return f.sort_values("date")


def load_btc() -> pd.DataFrame:
    rows = []
    for p in sorted(C.RAW.glob("btc_klines_*.json")):
        rows += json.loads(p.read_text())
    # only closed daily candles: close_time (field 6) must be before the fetch time
    fetched_ms = min(pd.Timestamp(e["fetched_at"]).value // 10**6
                     for e in json.loads((C.RAW / "fetch_log.json").read_text()) if e["file"].startswith("btc_"))
    rows = [r for r in rows if r[6] < fetched_ms]
    b = pd.DataFrame({
        "date": pd.to_datetime([r[0] for r in rows], unit="ms", utc=True).date,
        "btc_close": [float(r[4]) for r in rows],
    }).drop_duplicates("date")
    return b.sort_values("date")


def episodes(fng: pd.Series, cond, reset_days: int = 14) -> int:
    """First day in the zone after at least reset_days consecutive days outside (the brief's definition)."""
    n, outside = 0, reset_days  # the series starts "outside", so the first day in the zone counts
    for inside in cond(fng):
        if inside:
            if outside >= reset_days:
                n += 1
            outside = 0
        else:
            outside += 1
    return n


def gaps(dates: pd.Series) -> list[dict]:
    d = pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
    step = d.diff().dt.days
    return [{"after": d[i - 1].date().isoformat(), "missing_days": int(step[i] - 1)} for i in step.index if step[i] > 1]


def main():
    fng, btc = load_fng(), load_btc()
    df = fng.merge(btc, on="date", how="left")
    df.to_csv(C.PRIVATE / "daily.csv", index=False)
    # the whole BTC series (from 2017-08-17), so trailing returns also exist for the index's first days
    btc.to_csv(C.PRIVATE / "btc_daily.csv", index=False)

    F = C.F
    F.add("data.fng_first", str(fng.date.min()), "First Fear & Greed day", SRC)
    F.add("data.fng_last", str(fng.date.max()), "Last Fear & Greed day", SRC)
    F.add("data.fng_days", len(fng), "Days with an index value", SRC)
    g = gaps(fng.date)
    F.add("data.fng_missing_days", sum(x["missing_days"] for x in g), "Calendar days without an index value", SRC)
    (C.RESULTS / "fng_gaps.json").write_text(json.dumps(g, indent=2) + "\n")
    F.add("data.btc_first", str(btc.date.min()), "First BTCUSDT day (Binance)", SRC)
    F.add("data.btc_last", str(btc.date.max()), "Last BTCUSDT day (Binance)", SRC)
    F.add("data.btc_missing_days", sum(x["missing_days"] for x in gaps(btc.date)), "BTC days without a closing price", SRC)
    F.add("data.fng_days_without_btc", int(df.btc_close.isna().sum()),
          "Index days without a closed BTC close (e.g. today)", SRC)

    # How many days fall in each zone under the two threshold definitions to choose between
    zones = {"fear_le25": lambda v: v <= 25, "fear_lt20": lambda v: v < 20,
             "greed_ge76": lambda v: v >= 76, "greed_gt80": lambda v: v > 80}
    for name, cond in zones.items():
        F.add(f"data.zone_days.{name}", int(cond(df.fng).sum()), f"Days in zone {name}", SRC)
        F.add(f"data.episodes_14d.{name}", episodes(df.fng, cond), f"Episodes in zone {name} (14-day reset)", SRC)
    labels = df.groupby("fng_label").fng.agg(["min", "max"])
    for lbl, r in labels.iterrows():
        key = lbl.lower().replace(" ", "_")
        F.add(f"data.label_range.{key}.min", int(r["min"]), f"Lowest value with the label '{lbl}'", SRC)
        F.add(f"data.label_range.{key}.max", int(r["max"]), f"Highest value with the label '{lbl}'", SRC)
    F.save()
    print(df.tail(3).to_string(index=False))
    print(f"{len(df)} days, {int(df.btc_close.isna().sum())} without BTC price, gaps in F&G: {g}")


if __name__ == "__main__":
    main()
