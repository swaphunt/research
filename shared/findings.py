"""Write key figures to a study's data/results/findings.json.

Each number is stored as a leaf with value, description and source:

    {"a": {"share_positive": {"value": 0.297, "desc": "Share of bots in profit", "source": "scripts/03_analysis.py"}}}

Scripts run separately, so the file is loaded and updated instead of overwritten.
Keys are dot paths ("a.share_positive") that FINDINGS.md refers to.
"""
import json
import math
from datetime import date, datetime
from pathlib import Path


def _plain(v):
    """Convert numpy/pandas types to JSON-friendly Python types."""
    if hasattr(v, "item") and not isinstance(v, (list, dict, str)):
        v = v.item()
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, float) and not math.isfinite(v):
        raise ValueError(f"non-finite number cannot be stored as a key figure: {v}")
    return v


class Findings:
    def __init__(self, path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def add(self, key: str, value, desc: str, source: str):
        """Store one key figure under the dot path `key`. `source` is the script or query."""
        node = self.data
        *parents, leaf = key.split(".")
        for p in parents:
            node = node.setdefault(p, {})
            if "value" in node:
                raise KeyError(f"'{p}' in '{key}' is already a key figure")
        node[leaf] = {"value": _plain(value), "desc": desc, "source": str(source)}
        return value

    def get(self, key: str):
        node = self.data
        for p in key.split("."):
            node = node[p]
        return node["value"]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False) + "\n")
