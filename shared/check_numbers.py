"""Check that every number in article.md and FINDINGS.md can be traced to findings.json.

Usage:  python shared/check_numbers.py <study-dir>

Each numeric leaf in findings.json is expanded into the formats the article uses
(rounding, thousands separator, percent, absolute value, K/M/B). Numbers in the text that
do not match are listed for manual review. Years, dates, clock times, single digits, list numbers,
code spans and code blocks are ignored.

Numbers that are not results go in data/results/allowed_numbers.json:
    {"constants": ["0.1"], "brief": ["46"]}
"constants" are definitions (fees, thresholds), "brief" are the brief's expectations,
which FINDINGS.md quotes in order to test them. Both must be strings exactly as they appear in the text.
Exits with code 1 if there are numbers without a source.
"""
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

NUM = re.compile(r"(?<![\w.])[-−]?\$?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?")


def leaves(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("desc", "source"):
                continue
            yield from leaves(v)
    elif isinstance(o, list):
        for v in o:
            yield from leaves(v)
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        yield o


def variants(x) -> set:
    out = set()
    d = Decimal(repr(x))
    scaled = {d, d * 100, d / 1000, d / 1_000_000, d / 1_000_000_000}
    for v in scaled | {abs(s) for s in scaled}:
        for nd in (0, 1, 2, 3, 4):
            # both mathematical rounding and Python's float formatting (0.8135 → "81.3" with :.1%)
            for q in (v.quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP),
                      Decimal(f"{float(v):.{nd}f}")):
                s = f"{q:,.{nd}f}"
                out.add(s)
                out.add(s.replace(",", ""))
    return out


def strip(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\d{4}-\d{2}-\d{2}(T[\d:]+Z?)?", "", text)
    text = re.sub(r"(?<![\d.])\d{1,2}:\d{2}(:\d{2})?(?![\d.])", "", text)  # clock times
    text = re.sub(r"\]\([^)]*\)", "]", text)  # link and image paths
    text = re.sub(r"`[^`]*`", "", text)  # code spans (file names, keys)
    text = re.sub(r"(?m)^\s*\d+\.\s", "", text)  # list numbers
    text = re.sub(r"(?m)^#+\s*\d+[.)]?\s", "", text)  # numbered headings
    return text


def check(study: Path) -> list:
    results = study / "data" / "results"
    ok = set()
    for x in leaves(json.loads((results / "findings.json").read_text())):
        ok |= variants(x)
    allowed_file = results / "allowed_numbers.json"
    if allowed_file.exists():
        for vals in json.loads(allowed_file.read_text()).values():
            ok |= set(vals)

    bad = []
    for name in ("article.md", "FINDINGS.md"):
        f = study / name
        if not f.exists():
            continue
        for ln, line in enumerate(strip(f.read_text()).splitlines(), 1):
            for m in NUM.finditer(line):
                s = m.group(1) + (m.group(2) or "")
                if s in ok or re.fullmatch(r"\d|(19|20)\d\d", s):
                    continue
                bad.append((name, ln, s, line.strip()[:110]))
    return bad


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    bad = check(Path(argv[1]))
    for name, ln, s, ctx in bad:
        print(f"{name}:{ln}: '{s}'  …{ctx}")
    print(f"\n{len(bad)} numbers not traced to findings.json")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
