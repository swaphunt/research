"""Charts for the article (PNG + SVG) using shared/chartstyle.py.

1. 01_main: median return per horizon for Extreme Fear, all days and the same drop without Extreme Fear
2. 02_timeline: BTC price with the 27 episodes marked
3. 03_episodes_180d: 180-day return per episode, 2018 highlighted

Input: data/results/findings.json, episodes.csv, btc_daily.csv. Output: charts/*.png and *.svg.
Colours per docs/STYLE.md: accent only for what the chart is about; everything else in grey.
"""
import json

import matplotlib.ticker as mt
import numpy as np
import pandas as pd

import common as C
import chartstyle as cs

SOURCE = "Source: alternative.me Fear & Greed Index, Binance BTCUSDT daily close · data: 1 Feb 2018 – 28 Oct 2026"
SITE = "swaphunt.dev"
HORIZONS = (7, 30, 90, 180)
INK = cs.INK


def v(F, path):
    node = F
    for p in path.split("."):
        node = node[p]
    return node["value"]


def pct(x, nd=0):
    s = f"{abs(x) * 100:.{nd}f}%"
    return ("−" if x < 0 else "+") + s if round(x * 100, nd) != 0 else s


def pct_axis(ax, axis="y"):
    fmt = mt.FuncFormatter(lambda x, _: pct(x) if x != 0 else "0%")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def chart_main(F):
    P = "results.label.fear.reset14"
    groups = [
        ("Extreme Fear episodes", cs.ACCENT,
         [v(F, f"{P}.r{h}.median") for h in HORIZONS],
         [(v(F, f"{P}.r{h}.ci_lo"), v(F, f"{P}.r{h}.ci_hi")) for h in HORIZONS]),
        ("Same 30-day drop, no Extreme Fear", INK,
         [v(F, f"{P}.r{h}.matched_median") for h in HORIZONS],
         [(v(F, f"{P}.r{h}.matched_ci_lo"), v(F, f"{P}.r{h}.matched_ci_hi")) for h in HORIZONS]),
        ("All days", cs.GREY,
         [v(F, f"baseline.all_days.r{h}.median") for h in HORIZONS],
         [(v(F, f"baseline.all_days.r{h}.ci_lo"), v(F, f"baseline.all_days.r{h}.ci_hi")) for h in HORIZONS]),
    ]
    fig, ax = cs.figure()
    fig.subplots_adjust(top=0.78)
    x = np.arange(len(HORIZONS))
    handles = []
    offsets = (-0.22, 0, 0.22)
    for (label, color, med, ci), off in zip(groups, offsets):
        xs = x + off
        for xi, (lo, hi) in zip(xs, ci):
            ax.plot([xi, xi], [lo, hi], color=color, linewidth=2, solid_capstyle="round", alpha=0.55)
        handles.append(ax.scatter(xs, med, s=70, color=color, zorder=3, edgecolor=cs.BG, linewidth=2, label=label))
    # legend row above the plot (three groups, no overlap between end labels)
    leg = ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.02), ncol=3, frameon=False,
                    fontsize=10, handletextpad=0.4, columnspacing=1.6, borderaxespad=0)
    for t, h in zip(leg.get_texts(), handles):
        if h.get_label().startswith("Extreme"):
            t.set_color(cs.ACCENT)
            t.set_fontweight("semibold")
    for xi, m in zip(x + offsets[0], groups[0][2]):
        ax.annotate(pct(m, 1), (xi, m), xytext=(-8, 0), textcoords="offset points", ha="right", va="center",
                    fontsize=9, color=cs.ACCENT, family="IBM Plex Mono",
                    bbox=dict(boxstyle="square,pad=0.15", facecolor=cs.BG, edgecolor="none"))
    cs.zero_line(ax)
    ax.set_xticks(x, [f"{h} days" for h in HORIZONS])
    ax.set_xlim(-0.6, len(HORIZONS) - 0.4)
    pct_axis(ax)
    ax.grid(axis="x", visible=False)
    cs.mono_ticks(ax)
    ax.set_xlabel("Days after the signal", color=cs.GREY, fontsize=10)
    cs.frame(fig, "Extreme Fear did no better than the same drop without it",
             f"Median BTC return after the signal day, with 95% interval · "
             f"{v(F, P + '.episodes')} Extreme Fear episodes (index ≤ 25)", SOURCE, SITE)
    cs.save(fig, C.CHARTS / "01_main")


def chart_timeline(F, ep, btc):
    fig, ax = cs.figure()
    b = btc[btc.date >= "2018-01-01"]
    ax.plot(b.date, b.btc_close, color=cs.LIGHT, linewidth=1.6, zorder=1)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda y, _: f"${y / 1000:,.0f}k"))
    ax.yaxis.set_minor_formatter(mt.NullFormatter())
    ax.set_yticks([5000, 10000, 20000, 50000, 100000])
    e = ep[ep.zone == "fear"].merge(btc, on="date")
    ax.scatter(e.date, e.btc_close, s=60, color=cs.ACCENT, zorder=3, edgecolor=cs.BG, linewidth=2)
    by = {int(k[1:]): n["value"] for k, n in F["results"]["label"]["fear"]["reset14"]["episodes_by_year"].items()}
    for year, n in by.items():
        ys = e[e.year == year]
        if n >= 5:  # only the densest years get a label
            ax.annotate(f"{n} in {year}", (ys.date.mean(), ys.btc_close.min()), xytext=(0, -30),
                        textcoords="offset points", ha="center", fontsize=9.5, color=cs.ACCENT,
                        family="IBM Plex Mono")
    ax.grid(axis="x", visible=False)
    cs.mono_ticks(ax)
    cs.frame(fig, "Most Extreme Fear episodes came in 2018, 2019 and 2022",
             f"BTC price (log scale) with the first day of each of the "
             f"{v(F, 'results.label.fear.reset14.episodes')} Extreme Fear episodes marked", SOURCE, SITE)
    cs.save(fig, C.CHARTS / "02_timeline")


def chart_episodes(F, ep):
    P = "results.label.fear.reset14.r180"
    e = ep[(ep.zone == "fear") & ep.r180.notna()].copy()
    fig, ax = cs.figure()
    is18 = e.year == 2018
    ax.scatter(e[~is18].date, e[~is18].r180, s=60, color=cs.GREY, zorder=3, edgecolor=cs.BG, linewidth=2)
    ax.scatter(e[is18].date, e[is18].r180, s=70, color=cs.ACCENT, zorder=4, edgecolor=cs.BG, linewidth=2)
    med, loo = v(F, f"{P}.median"), v(F, f"{P}.loo_max")
    assert v(F, f"{P}.loo_max_year") == 2018
    ax.axhline(med, color=cs.ACCENT, linewidth=1.5)
    ax.axhline(loo, color=INK, linewidth=1.2, linestyle=(0, (4, 3)))
    right = e.date.max() + pd.Timedelta(days=40)
    ax.annotate(f"median, all {len(e)}: {pct(med, 1)}", (right, med), xytext=(0, -12), textcoords="offset points",
                ha="right", fontsize=9.5, color=cs.ACCENT, family="IBM Plex Mono")
    ax.annotate(f"median without 2018: {pct(loo, 1)}", (right, loo), xytext=(0, -12), textcoords="offset points",
                ha="right", va="top", fontsize=9.5, color=INK, family="IBM Plex Mono")
    ax.annotate("2018", (e[is18].date.mean(), e[is18].r180.min()), xytext=(0, -18), textcoords="offset points",
                ha="center", fontsize=10, color=cs.ACCENT, fontweight="semibold")
    cs.zero_line(ax)
    pct_axis(ax)
    ax.grid(axis="x", visible=False)
    cs.mono_ticks(ax)
    cs.frame(fig, "Six 2018 episodes pull the 180-day median below zero",
             "BTC return 180 days after each Extreme Fear episode (index ≤ 25)", SOURCE, SITE)
    cs.save(fig, C.CHARTS / "03_episodes_180d")


def main():
    cs.setup()
    F = json.loads((C.RESULTS / "findings.json").read_text())
    ep = pd.read_csv(C.RESULTS / "episodes.csv", parse_dates=["date"])
    btc = pd.read_csv(C.PRIVATE / "btc_daily.csv", parse_dates=["date"])
    chart_main(F)
    chart_timeline(F, ep, btc)
    chart_episodes(F, ep)
    print("charts:", sorted(p.name for p in C.CHARTS.glob("*.png")))


if __name__ == "__main__":
    main()
