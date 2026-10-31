"""Read the collectors' snapshots from the NAS (collectors/research_collectors/storage.py).

    import snapshots
    ep = snapshots.load("x402_market", "endpoints")              # all periods, with the column 'period'
    ep = snapshots.load("x402_market", "endpoints", periods=["2026-10-29"])

RESEARCH_DATA_DIR points to the data directory (required; no default, so no local path in the code).
Per period the first successful snapshot (<period>/) is used. Manual reruns are stored
as <period>__run<id>/ and are only included if asked for (all_runs=True).
"""
import json
import os
from pathlib import Path

import pandas as pd

def data_dir() -> Path:
    try:
        return Path(os.environ["RESEARCH_DATA_DIR"])
    except KeyError:
        raise RuntimeError("environment variable RESEARCH_DATA_DIR is not set") from None


def snapshot_dirs(collector: str, all_runs: bool = False) -> list[Path]:
    root = data_dir() / collector
    out = []
    for d in sorted(root.iterdir()) if root.exists() else []:
        if d.name.startswith((".", "_")) or not (d / "manifest.json").exists():
            continue
        if "__" in d.name and not all_runs:
            continue
        if json.loads((d / "manifest.json").read_text()).get("status") == "success":
            out.append(d)
    return out


def manifest(snapshot: Path) -> dict:
    return json.loads((Path(snapshot) / "manifest.json").read_text())


def load(collector: str, table: str, periods=None, all_runs: bool = False) -> pd.DataFrame:
    frames = []
    for d in snapshot_dirs(collector, all_runs):
        period = d.name.split("__")[0]
        if periods is not None and period not in periods:
            continue
        # nullable types: NULL stays NULL, and integers do not become float
        df = pd.read_parquet(d / f"{table}.parquet", dtype_backend="numpy_nullable")
        df.insert(0, "period", period)
        if all_runs:
            df.insert(1, "snapshot", d.name)
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"no snapshots of {collector}/{table} in {data_dir()}")
    return pd.concat(frames, ignore_index=True)
