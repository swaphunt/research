"""Shared chart style per docs/STYLE.md: 2000 × 1120 px PNG + SVG.

    import chartstyle as cs
    cs.setup()
    fig, ax = cs.figure()
    ...
    cs.frame(fig, "Random entries beat the real bots", "Net PnL per bot, USD",
             source="Source: SwapHunt paper trades, 31 Jan – 25 Oct 2026", site="swaphunt.dev")
    cs.save(fig, CHARTS / "distribution")
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

BG, INK, ACCENT, GREY, LIGHT, GRID = "#FAFAF7", "#1A1D21", "#2F6FEB", "#8B8F98", "#D6D7DB", "#ECEDEF"
SITES = ("swaphunt.dev", "lookproof.dev", "senderward.com")
FONTS = Path(__file__).resolve().parent / "fonts"
FIGSIZE, DPI = (10, 5.6), 200  # = 2000 × 1120 px


def setup():
    for f in FONTS.glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))
    plt.rcParams.update({
        "font.family": "IBM Plex Sans", "font.size": 11,
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
        "axes.edgecolor": LIGHT, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": GREY, "ytick.color": GREY, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
        "svg.fonttype": "none", "text.parse_math": False, "axes.unicode_minus": True,
        "svg.hashsalt": "research",  # fixed ids in SVG, so the same chart gives the same file
    })


def figure(**kw):
    fig, ax = plt.subplots(figsize=FIGSIZE, **kw)
    fig.subplots_adjust(top=0.82, bottom=0.17, left=0.08, right=0.95)
    return fig, ax


def frame(fig, title: str, subtitle: str, source: str, site: str):
    """Title (= the conclusion), subtitle, source bottom left and site in accent colour on the right."""
    if site not in SITES:
        raise ValueError(f"unknown site: {site}")
    fig.text(0.06, 0.965, title, fontsize=15, fontweight="semibold", va="top")
    fig.text(0.06, 0.905, subtitle, fontsize=10.5, color=GREY, va="top")
    fig.text(0.06, 0.025, source, fontsize=8.5, color=GREY, family="IBM Plex Mono")
    fig.text(0.94, 0.025, site, fontsize=9, color=ACCENT, ha="right", family="IBM Plex Mono",
             fontweight="medium")


def mono_ticks(ax):
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_family("IBM Plex Mono")
        lbl.set_fontsize(9)


def zero_line(ax, y=0, **kw):
    """Break-even/zero as a dashed line."""
    ax.axhline(y, color=GREY, linestyle="--", linewidth=1, **kw)


def save(fig, path):
    """Save as <path>.png and <path>.svg."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # no timestamps in metadata, so reruns do not produce new files in git
    fig.savefig(path.with_suffix(".png"), dpi=DPI, metadata={"Software": None})
    fig.savefig(path.with_suffix(".svg"), metadata={"Date": None})
    plt.close(fig)
