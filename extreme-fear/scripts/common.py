"""Paths and shared helpers for the study. Import with `import common as C` in every script."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RESULTS = ROOT / "data" / "results"
PRIVATE = RESULTS / "private"  # near-raw or per-domain files; never exported to the public repo
CHARTS = ROOT / "charts"
PRIVATE.mkdir(parents=True, exist_ok=True)

# shared/ (chartstyle, db, findings) lives in the repo root: two levels above the study in the monorepo,
# one level in the public repo. Search upwards so the same code works in both places.
SHARED = next(p / "shared" for p in ROOT.parents if (p / "shared").is_dir())
sys.path.insert(0, str(SHARED))

from findings import Findings  # noqa: E402

F = Findings(RESULTS / "findings.json")
