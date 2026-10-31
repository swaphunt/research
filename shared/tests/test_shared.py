import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_numbers  # noqa: E402
from findings import Findings  # noqa: E402


def make_study(tmp_path, findings, article, allowed=None):
    res = tmp_path / "data" / "results"
    res.mkdir(parents=True)
    (res / "findings.json").write_text(json.dumps(findings))
    if allowed:
        (res / "allowed_numbers.json").write_text(json.dumps(allowed))
    (tmp_path / "article.md").write_text(article)
    return tmp_path


def test_findings_roundtrip(tmp_path):
    p = tmp_path / "findings.json"
    F = Findings(p)
    F.add("a.share", 0.2971, "Share in profit", "scripts/03.py")
    F.save()
    F2 = Findings(p)
    F2.add("b.n", 3650, "Number of bots", "scripts/00.py")
    F2.save()
    data = json.loads(p.read_text())
    assert data["a"]["share"] == {"value": 0.2971, "desc": "Share in profit", "source": "scripts/03.py"}
    assert Findings(p).get("b.n") == 3650


def test_findings_rejects_nan(tmp_path):
    with pytest.raises(ValueError):
        Findings(tmp_path / "f.json").add("x", float("nan"), "d", "s")


def test_findings_numpy_types(tmp_path):
    np = pytest.importorskip("numpy")
    F = Findings(tmp_path / "f.json")
    F.add("x", np.float64(1.5), "d", "s")
    F.add("y", np.int64(7), "d", "s")
    F.save()
    assert json.loads((tmp_path / "f.json").read_text())["y"]["value"] == 7


def test_formats_are_traced(tmp_path):
    f = {"a": {"value": 0.2971}, "n": {"value": 2714058}, "m": {"value": 2700000}, "c": {"value": -1.35}}
    s = make_study(tmp_path, f, "29.7% of bots, 2,714,058 trades, 2.7M rows, lost $1.35 or −1.35.")
    assert check_numbers.check(s) == []


def test_untraced_number_is_reported(tmp_path):
    s = make_study(tmp_path, {"a": {"value": 0.5}}, "Half (50%) of them, but 46 were wrong.")
    bad = check_numbers.check(s)
    assert [b[2] for b in bad] == ["46"]


def test_ignores_dates_years_code_and_lists(tmp_path):
    text = "1. Data from 2026-10-26 in 2026.\n`top_500` and ```\n123\n```\n3 bots"
    s = make_study(tmp_path, {}, text)
    assert check_numbers.check(s) == []


def test_desc_numbers_do_not_count_as_sources(tmp_path):
    f = {"a": {"value": 1.0, "desc": "top 500", "source": "scripts/03_x.py"}}
    s = make_study(tmp_path, f, "the top 500")
    assert [b[2] for b in check_numbers.check(s)] == ["500"]


def test_allowed_numbers(tmp_path):
    s = make_study(tmp_path, {}, "brief expected 46%, fee 0.1%", {"brief": ["46"], "constants": ["0.1"]})
    assert check_numbers.check(s) == []


def test_chartstyle_size_and_fonts(tmp_path):
    import chartstyle as cs
    from matplotlib import font_manager
    from matplotlib.image import imread

    cs.setup()
    names = {f.name for f in font_manager.fontManager.ttflist}
    assert {"IBM Plex Sans", "IBM Plex Mono"} <= names
    fig, ax = cs.figure()
    ax.bar(["a", "b"], [1, -1], color=[cs.ACCENT, cs.LIGHT])
    cs.zero_line(ax)
    cs.mono_ticks(ax)
    cs.frame(fig, "Title", "Subtitle", source="Source: test, 1 Jan – 2 Jan 2026", site="lookproof.dev")
    cs.save(fig, tmp_path / "c")
    h, w = imread(tmp_path / "c.png").shape[:2]
    assert (w, h) == (2000, 1120)
    assert (tmp_path / "c.svg").exists()


def test_python_float_rounding_is_accepted(tmp_path):
    s = make_study(tmp_path, {"a": {"value": 0.8135}}, f"{0.8135:.1%} or 81.4%")
    assert check_numbers.check(s) == []


def test_snapshots_load(tmp_path, monkeypatch):
    pd = pytest.importorskip("pandas")
    import snapshots

    monkeypatch.setenv("RESEARCH_DATA_DIR", str(tmp_path))
    for name, status, val in [("2026-10-28", "success", 1), ("2026-10-29", "success", 2),
                              ("2026-10-29__run7", "success", 3), ("2026-10-30", "failed", 4)]:
        d = tmp_path / "c" / name
        d.mkdir(parents=True)
        (d / "manifest.json").write_text(json.dumps({"status": status}))
        pd.DataFrame({"x": [val]}).to_parquet(d / "t.parquet")
    (tmp_path / "c" / "_failed").mkdir()
    df = snapshots.load("c", "t")
    assert df.to_dict("records") == [{"period": "2026-10-28", "x": 1}, {"period": "2026-10-29", "x": 2}]
    assert len(snapshots.load("c", "t", all_runs=True)) == 3
    assert snapshots.load("c", "t", periods=["2026-10-29"]).x.tolist() == [2]


def test_clock_times_are_ignored(tmp_path):
    s = make_study(tmp_path, {}, "published at 00:00 UTC, updated 14:30:15")
    assert check_numbers.check(s) == []
