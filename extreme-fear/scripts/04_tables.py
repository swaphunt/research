"""Table of all Extreme Fear episodes for the article, generated from findings.json.

Output: data/results/episodes_table.md (inserted into article.md under "Every episode").
"""
import json

import common as C

HORIZONS = (7, 30, 90, 180)


def pct(x):
    if x is None:
        return "–"
    s = f"{abs(x) * 100:.1f}%"
    return s if round(x * 100, 1) == 0 else ("−" if x < 0 else "+") + s


def main():
    F = json.loads((C.RESULTS / "findings.json").read_text())
    eps = F["results"]["label"]["fear"]["reset14"]["episode"]
    lines = ["| Date | Index | BTC change, previous 30 days | 7 days | 30 days | 90 days | 180 days |",
             "|---|---|---|---|---|---|---|"]
    for key in sorted(eps):
        e = eps[key]
        date = f"{key[1:5]}-{key[5:7]}-{key[7:9]}"
        val = lambda k: e[k]["value"] if k in e else None
        lines.append(f"| {date} | {val('fng')} | {pct(val('trail30'))} | "
                     + " | ".join(pct(val(f"r{h}")) for h in HORIZONS) + " |")
    out = "\n".join(lines) + "\n"
    (C.RESULTS / "episodes_table.md").write_text(out)
    print(f"{len(eps)} episodes written to episodes_table.md")


if __name__ == "__main__":
    main()
