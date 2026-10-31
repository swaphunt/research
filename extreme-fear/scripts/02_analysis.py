"""Forward BTC returns after Extreme Fear / Extreme Greed episodes against three baselines.

Definitions (approved at review 2026-10-29, locked before returns were seen):
- Zones: primarily the index's labels (fear <= 25, greed >= 76); robustness the brief's (< 20, > 80).
- Episode: first day in the zone after at least RESET index days outside. Primary 14, robustness 7 and 30.
- Return: close(d+h) / close(d) - 1 for h in HORIZONS calendar days; entry = close on the signal day.
- Baselines:
  1. all index days,
  2. 10,000 draws of n random index days (n = number of episodes),
  3. matched: per episode one random day outside the zone whose 30-day trailing return is
     within +-MATCH_TOL of the episode's; 10,000 repetitions.
- Uncertainty: 95% bootstrap interval on the median (10,000 resamples of the episodes).
- Leave-one-year-out: the median with each calendar year removed.
Seed is fixed, so all numbers can be reproduced.

Output: data/results/episodes.csv, data/results/summary.csv and results.* in findings.json.
"""
import numpy as np
import pandas as pd

import common as C

SRC = "scripts/02_analysis.py"
HORIZONS = (7, 30, 90, 180)
TRAIL = 30
MATCH_TOL = 0.05  # +-5 percentage points on 30-day trailing return
N_DRAWS = 10_000
SEED = 20261029

ZONES = {
    ("label", "fear"): lambda v: v <= 25,
    ("label", "greed"): lambda v: v >= 76,
    ("brief", "fear"): lambda v: v < 20,
    ("brief", "greed"): lambda v: v > 80,
}
RESETS = (14, 7, 30)
PRIMARY = ("label", 14)


def load() -> pd.DataFrame:
    d = pd.read_csv(C.PRIVATE / "daily.csv", parse_dates=["date"]).set_index("date")
    # the whole BTC series (also before the index start), otherwise trailing returns are missing for the first episodes
    btc = pd.read_csv(C.PRIVATE / "btc_daily.csv", parse_dates=["date"]).set_index("date").btc_close
    for h in HORIZONS:
        d[f"r{h}"] = btc.shift(-h, freq="D").reindex(d.index) / d.btc_close - 1
    d["trail30"] = d.btc_close / btc.shift(TRAIL, freq="D").reindex(d.index) - 1
    return d


def episode_days(fng: pd.Series, cond, reset: int) -> pd.DatetimeIndex:
    out, outside = [], reset
    for day, inside in cond(fng).items():
        if inside:
            if outside >= reset:
                out.append(day)
            outside = 0
        else:
            outside += 1
    return pd.DatetimeIndex(out)


def stats(x: np.ndarray) -> dict:
    return {"n": int(len(x)), "median": float(np.median(x)), "p10": float(np.percentile(x, 10)),
            "p90": float(np.percentile(x, 90)), "share_positive": float(np.mean(x > 0)), "worst": float(x.min())}


def boot_ci(x: np.ndarray, rng) -> tuple[float, float]:
    med = np.median(rng.choice(x, size=(N_DRAWS, len(x)), replace=True), axis=1)
    return float(np.percentile(med, 2.5)), float(np.percentile(med, 97.5))


def random_pctile(x: np.ndarray, pool: np.ndarray, rng) -> float:
    """Share of random draws (n days without replacement) whose median is lower than the episodes'."""
    idx = np.argsort(rng.random((N_DRAWS, len(pool))), axis=1)[:, : len(x)]
    med = np.median(pool[idx], axis=1)
    return float(np.mean(med < np.median(x)))


def matched(d: pd.DataFrame, ep: pd.DatetimeIndex, h: int, in_zone: pd.Series, rng, exclude=None, full=False):
    """Matched baseline. Returns (median of matched days, percentile, smallest candidate pool),
    and with full=True also the 95% interval of the matched medians. exclude: days that may not be candidates."""
    col = f"r{h}"
    ok = (~in_zone) & d[col].notna() & d.trail30.notna()
    if exclude is not None:
        ok &= ~exclude
    cand = d[ok]
    pools = []
    for day in ep:
        t = d.at[day, "trail30"]
        p = cand[(cand.trail30 - t).abs() <= MATCH_TOL][col].to_numpy()
        pools.append(p)
    if any(len(p) == 0 for p in pools):
        return (None, None, 0, None, None) if full else (None, None, 0)
    draws = np.column_stack([p[rng.integers(0, len(p), N_DRAWS)] for p in pools])
    med = np.median(draws, axis=1)
    ep_med = float(np.median(d.loc[ep, col]))
    out = (float(np.median(med)), float(np.mean(med < ep_med)), int(min(len(p) for p in pools)))
    if full:
        out += (float(np.percentile(med, 2.5)), float(np.percentile(med, 97.5)))
    return out


def matched_near_share(d: pd.DataFrame, ep: pd.DatetimeIndex, h: int, in_zone: pd.Series, near_mask: pd.Series):
    """Expected share of matched days that fall in near_mask: each episode draws one day uniformly from its
    candidate pool, so the share is the mean over episodes of the pool's share in near_mask. No random draws."""
    col = f"r{h}"
    cand = d[(~in_zone) & d[col].notna() & d.trail30.notna()]
    shares = []
    for day in ep:
        p = cand[(cand.trail30 - d.at[day, "trail30"]).abs() <= MATCH_TOL]
        shares.append(float(near_mask[p.index].mean()))
    return float(np.mean(shares))


def near(index: pd.DatetimeIndex, days: pd.DatetimeIndex, window: int) -> pd.Series:
    """True for days within +-window calendar days of one of `days`."""
    m = pd.Series(False, index=index)
    for day in days:
        m |= (index >= day - pd.Timedelta(days=window)) & (index <= day + pd.Timedelta(days=window))
    return m


def extras(d: pd.DataFrame, F):
    """Added at review 2: intervals for the main chart and matched baseline without days near episodes.
    Own generator, so the already approved numbers do not move."""
    rng = np.random.default_rng(SEED + 1)
    for h in HORIZONS:
        allv = d[f"r{h}"].dropna().to_numpy()
        lo, hi = boot_ci(allv, rng)
        F.add(f"baseline.all_days.r{h}.ci_lo", lo, f"All days, {h} days: bootstrap 2.5%", SRC)
        F.add(f"baseline.all_days.r{h}.ci_hi", hi, f"All days, {h} days: bootstrap 97.5%", SRC)
    for zone in ("fear", "greed"):
        cond = ZONES[("label", zone)]
        in_zone = cond(d.fng)
        ep = episode_days(d.fng, cond, 14)
        key = f"results.label.{zone}.reset14"
        for excl_name, excl in (("", None), ("_excl14", near(d.index, ep, 14))):
            for h in HORIZONS:
                col = f"r{h}"
                e = ep[d.loc[ep, col].notna().to_numpy()]
                med, pct, pool, lo, hi = matched(d, e, h, in_zone, rng, exclude=excl, full=True)
                assert pool > 0, f"episode without matching days: {zone}{excl_name}/{h}"
                tag = f"{key}.r{h}.matched{excl_name}"
                if excl_name:
                    F.add(f"{tag}_median", med, f"Matched without days +-14 of episodes, {h} days: median", SRC)
                    F.add(f"{tag}_pctile", pct, f"Matched without days +-14 of episodes, {h} days: share lower", SRC)
                    F.add(f"{tag}_min_pool", pool, f"Matched without days +-14 of episodes, {h} days: smallest pool", SRC)
                F.add(f"{tag}_ci_lo", lo, f"Matched{excl_name}, {h} days: 2.5% of matched medians", SRC)
                F.add(f"{tag}_ci_hi", hi, f"Matched{excl_name}, {h} days: 97.5% of matched medians", SRC)
        # matched comparison without the 2018 episodes (does 2018 also carry the matched result?)
        if zone == "fear":
            rng18 = np.random.default_rng(SEED + 2)  # own generator: moves no other numbers
            ep_x18 = ep[ep.year != 2018]
            for h in HORIZONS:
                col = f"r{h}"
                e = ep_x18[d.loc[ep_x18, col].notna().to_numpy()]
                med, pct, pool, lo, hi = matched(d, e, h, in_zone, rng18, full=True)
                F.add(f"{key}.r{h}.no2018_median", float(np.median(d.loc[e, col])), f"Without 2018, {h} days: median", SRC)
                F.add(f"{key}.r{h}.no2018_matched_median", med, f"Without 2018, matched, {h} days: median", SRC)
                F.add(f"{key}.r{h}.no2018_matched_pctile", pct, f"Without 2018, matched, {h} days: share lower", SRC)
            F.add(f"{key}.episodes_no2018", len(ep_x18), "Fear episodes without 2018", SRC)
        share = float(near(d.index, ep, 14)[~in_zone].mean())
        F.add(f"{key}.share_nonzone_days_near_episode", share,
              "Share of days outside the zone that are within +-14 days of an episode", SRC)
        # added before publication: the same share among the matched days themselves (review 3)
        for h in HORIZONS:
            e = ep[d.loc[ep, f"r{h}"].notna().to_numpy()]
            F.add(f"{key}.r{h}.matched_share_near14", matched_near_share(d, e, h, in_zone, near(d.index, ep, 14)),
                  f"Matched, {h} days: expected share of matched days within +-14 days of an episode", SRC)


def main():
    rng = np.random.default_rng(SEED)
    d = load()
    F = C.F
    F.add("method.seed", SEED, "Seed for all random draws", SRC)
    F.add("method.match_tol", MATCH_TOL, "Tolerance on 30-day trailing return in matched baseline", SRC)
    F.add("method.n_draws", N_DRAWS, "Draws in bootstrap and baselines", SRC)

    for h in HORIZONS:
        allv = d[f"r{h}"].dropna().to_numpy()
        for k, v in stats(allv).items():
            F.add(f"baseline.all_days.r{h}.{k}", v, f"All index days, {h} days ahead: {k}", SRC)

    rows, ep_rows = [], []
    for (tset, zone), cond in ZONES.items():
        in_zone = cond(d.fng)
        for reset in RESETS:
            if tset == "brief" and reset != 14:
                continue  # robustness: other thresholds only with the primary reset
            ep = episode_days(d.fng, cond, reset)
            key = f"results.{tset}.{zone}.reset{reset}"
            F.add(f"{key}.episodes", len(ep), f"Episodes ({tset}, {zone}, {reset}-day reset)", SRC)
            for h in HORIZONS:
                col = f"r{h}"
                e = ep[d.loc[ep, col].notna().to_numpy()]
                x = d.loc[e, col].to_numpy()
                s = stats(x)
                s["ci_lo"], s["ci_hi"] = boot_ci(x, rng)
                pool = d[col].dropna().to_numpy()
                s["random_pctile"] = random_pctile(x, pool, rng)
                s["matched_median"], s["matched_pctile"], s["matched_min_pool"] = matched(d, e, h, in_zone, rng)
                assert s["matched_min_pool"] > 0, f"episode without matching days: {tset}/{zone}/{reset}/{h}"
                if (tset, reset) == PRIMARY:
                    years = pd.Series(e.year, index=e)
                    loo = {int(y): float(np.median(d.loc[e[years != y], col])) for y in sorted(set(e.year))
                           if (years != y).sum() > 0}
                    s["loo_min"], s["loo_max"] = min(loo.values()), max(loo.values())
                    s["loo_min_year"] = min(loo, key=loo.get)
                    s["loo_max_year"] = max(loo, key=loo.get)
                for k, v in s.items():
                    if v is not None:
                        F.add(f"{key}.r{h}.{k}", v, f"{tset}/{zone}/reset{reset}, {h} days ahead: {k}", SRC)
                rows.append({"thresholds": tset, "zone": zone, "reset": reset, "horizon": h, **s})
            if (tset, reset) == PRIMARY:
                for y, n in pd.Series(ep.year).value_counts().sort_index().items():
                    F.add(f"{key}.episodes_by_year.y{y}", int(n), f"Episodes in {y} ({zone})", SRC)
                for day in ep:
                    r = d.loc[day]
                    ek = f"{key}.episode.d{day.date().isoformat().replace('-', '')}"
                    F.add(f"{ek}.fng", int(r.fng), f"Index value on the episode day {day.date()}", SRC)
                    F.add(f"{ek}.trail30", float(r.trail30), f"30-day trailing return {day.date()}", SRC)
                    for h in HORIZONS:
                        if pd.notna(r[f"r{h}"]):
                            F.add(f"{ek}.r{h}", float(r[f"r{h}"]), f"{h}-day return after {day.date()}", SRC)
                    ep_rows.append({"zone": zone, "date": day.date(), "year": day.year, "fng": int(r.fng),
                                    "trail30": r.trail30, **{f"r{h}": r[f"r{h}"] for h in HORIZONS}})

    extras(d, F)
    pd.DataFrame(rows).to_csv(C.RESULTS / "summary.csv", index=False)
    pd.DataFrame(ep_rows).to_csv(C.RESULTS / "episodes.csv", index=False)
    F.save()
    show = pd.DataFrame(rows)
    show = show[(show.thresholds == "label") & (show.reset == 14)]
    print(show[["zone", "horizon", "n", "median", "ci_lo", "ci_hi", "share_positive", "random_pctile",
                "matched_median", "matched_pctile", "matched_min_pool"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
