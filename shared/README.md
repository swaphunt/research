# shared

Common code used by all studies. Studies import it rather than copy it; each study's `scripts/common.py` searches upwards for `shared/` and puts it on `sys.path`.

| File | What |
|---|---|
| `findings.py` | `Findings(path).add("a.share", 0.297, "description", source=__file__)` + `.save()`. Each key figure is stored with value, description and source. |
| `check_numbers.py` | `python shared/check_numbers.py <study>`: every number in `article.md` and `FINDINGS.md` must be found in `data/results/findings.json`. Definitions and the brief's figures go in `data/results/allowed_numbers.json` (`{"constants": [...], "brief": [...]}`). |
| `chartstyle.py` | Chart style: `setup()`, `figure()`, `frame(fig, title, subtitle, source=, site=)`, `zero_line()`, `mono_ticks()`, `save()` → PNG (2000 × 1120) + SVG. |
| `snapshots.py` | `load(collector, table)`: snapshots from our own data collectors as one DataFrame with the column `period`. Needs `RESEARCH_DATA_DIR`. |
| `db.py` | `connect()` / `query_df(sql)` against the database in `RESEARCH_DB_URL` (or another environment variable). |
| `fonts/` | IBM Plex Sans and Mono, SIL Open Font License 1.1 (`fonts/OFL.txt`). |

Tests: `python -m pytest shared/tests` from the repository root (needs pandas, numpy, matplotlib, pytest).
