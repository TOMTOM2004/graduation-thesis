"""CGPI source-vintage override (ITEM-025): default preserved, override read at call time."""

import zipfile
from pathlib import Path

import pandas as pd
import pytest

ENV = "CGPI_SOURCE_DIR"
REPO = Path(__file__).resolve().parents[1]


def _fake_prices(path: Path, value: float) -> None:
    pd.DataFrame(
        {
            "date": ["2025-01-01", "2025-02-01"],
            "group": ["energy", "energy"],
            "group_ja": ["x", "x"],
            "value": [value, value],
        }
    ).to_csv(path / "import_prices_extracted.csv", index=False)


VINTAGE = REPO / "data" / "source-vintages" / "boj-cgpi-20261013"
RAW_CGPI = REPO / "data" / "raw" / "boj-cgpi"


def test_default_dir_is_new_vintage(monkeypatch):
    """J2: unset env => the 2026-10-13 vintage, never the superseded data/raw snapshot."""
    from src.data.fetch_import_prices import cgpi_dir

    monkeypatch.delenv(ENV, raising=False)
    assert cgpi_dir() == VINTAGE
    assert (VINTAGE / "import_prices_extracted.csv").exists()


def test_explicit_override_can_select_old_raw_snapshot(monkeypatch):
    """Path resolution only; passes even when data/raw has no CGPI files (fresh clone)."""
    from src.data.fetch_import_prices import cgpi_dir, cgpi_import_path

    monkeypatch.setenv(ENV, str(RAW_CGPI))
    assert cgpi_dir() == RAW_CGPI
    assert cgpi_import_path() == RAW_CGPI / "import_prices_extracted.csv"


def test_canonical_vintage_matches_recorded_sha256sums():
    """The tracked vintage is verified against its own SHA256SUMS (no data/raw dependency)."""
    import hashlib

    lines = (VINTAGE / "SHA256SUMS").read_text().strip().splitlines()
    assert lines
    for line in lines:
        sha, name = line.split(maxsplit=1)
        assert hashlib.sha256((VINTAGE / name.strip()).read_bytes()).hexdigest() == sha, name


def test_override_dir_resolved_at_call_time(monkeypatch, tmp_path):
    from src.data.fetch_import_prices import cgpi_dir

    monkeypatch.setenv(ENV, str(tmp_path))
    assert cgpi_dir() == tmp_path


def test_all_import_price_readers_follow_override(monkeypatch, tmp_path):
    _fake_prices(tmp_path, 777.0)
    monkeypatch.setenv(ENV, str(tmp_path))

    from src.analysis import cost_push_panel, io_price_model, oil_lp_prep, trade_loss

    assert trade_loss.load_import_prices()["value"].eq(777.0).all()
    assert oil_lp_prep.cgpi_import_path() == tmp_path / "import_prices_extracted.csv"
    assert io_price_model.cgpi_import_path() == tmp_path / "import_prices_extracted.csv"
    assert cost_push_panel.cgpi_import_path() == tmp_path / "import_prices_extracted.csv"


def test_trade_loss_default_reader_uses_new_vintage(monkeypatch):
    from src.analysis import trade_loss

    monkeypatch.delenv(ENV, raising=False)
    assert trade_loss.cgpi_import_path() == VINTAGE / "import_prices_extracted.csv"


def test_override_never_downloads_missing_zip(monkeypatch, tmp_path):
    from src.data import fetch_import_prices as f

    monkeypatch.setenv(ENV, str(tmp_path))
    assert not hasattr(f, "httpx")  # no network client in this module
    with pytest.raises(FileNotFoundError, match="cgpi_m_jp.zip"):
        f.fetch_cgpi_bulk()
    with pytest.raises(FileNotFoundError, match="cgpilink1.csv"):
        f.fetch_cgpi_link()


def test_override_extraction_writes_only_inside_override(monkeypatch, tmp_path):
    """Extraction from an override dir must cache beside the source, never in data/raw."""
    from src.data import fetch_import_prices as f

    code = f.IMPORT_PRICE_SERIES["energy"]["code"]
    header = "code,desc,cat,202001,202002\n"
    row = f"{code},e,c,100.0,101.0\n"
    link = tmp_path / "cgpilink1.csv"
    link.write_bytes((header + row).encode("shift_jis"))
    zpath = tmp_path / "cgpi_m_jp.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("cgpi.csv", (header + row).encode("shift_jis"))

    monkeypatch.setenv(ENV, str(tmp_path))
    df = f.extract_import_prices()
    assert (tmp_path / "import_prices_extracted.csv").exists()
    assert set(df["group"]) == {"energy"}


def test_gdp_ratio_uses_matching_year():
    from src.analysis.trade_loss import GDP_BN_BY_YEAR, add_gdp_pct

    assert GDP_BN_BY_YEAR[2022] == 584_501.3
    assert GDP_BN_BY_YEAR[2023] == 616_659.4
    assert GDP_BN_BY_YEAR[2024] == 636_893.3
    assert GDP_BN_BY_YEAR[2025] == 666_440.7

    df = pd.DataFrame(
        {"year": [2022, 2025], "total_corrected_bn_jpy": [35_000.0, 24_712.0]}
    )
    out = add_gdp_pct(df)
    assert out.loc[0, "gdp_pct"] == pytest.approx(35_000.0 / 584_501.3 * 100)
    assert out.loc[1, "gdp_pct"] == pytest.approx(24_712.0 / 666_440.7 * 100)
    assert out.loc[1, "gdp_pct"] != pytest.approx(24_712.0 / 584_501.3 * 100)


def test_gdp_ratio_missing_year_is_nan_not_error():
    from src.analysis.trade_loss import add_gdp_pct

    df = pd.DataFrame({"year": [2019], "total_corrected_bn_jpy": [1.0]})
    assert pd.isna(add_gdp_pct(df).loc[0, "gdp_pct"])


def test_total_trade_loss_cache_without_gdp_pct_is_upgraded(monkeypatch, tmp_path):
    """A same-vintage cache lacking gdp_pct (pre-ITEM-025 layout) gets it added, not a crash."""
    from src.analysis import trade_loss as t

    monkeypatch.setenv(ENV, str(_src_dir(tmp_path / "src")))
    monkeypatch.setattr(t, "TRADE_LOSS_DIR", tmp_path)
    pd.DataFrame(
        {"year": [2022, 2025], "total_corrected_bn_jpy": [35_000.0, 24_712.0]}
    ).to_csv(tmp_path / "trade_loss_total.csv", index=False)
    (tmp_path / "trade_loss_total.csv.srcsha").write_text(t.cgpi_source_fingerprint())
    out = t.compute_total_trade_loss(force=False)
    assert out.loc[out.year == 2025, "gdp_pct"].iloc[0] == pytest.approx(
        24_712.0 / 666_440.7 * 100
    )


def test_default_never_downloads_missing_files(monkeypatch, tmp_path):
    """Even without env, a missing file in the default dir must not trigger a download."""
    from src.data import fetch_import_prices as f

    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(f, "VINTAGE_DIR", tmp_path, raising=False)
    assert not hasattr(f, "httpx")  # no network client in this module
    with pytest.raises(FileNotFoundError):
        f.fetch_cgpi_bulk()


# ---- F-1: trade_loss caches are bound to the CGPI source fingerprint -------------------------


def _src_dir(path: Path, value: float = 150.0, domestic: float = 110.0) -> Path:
    path.mkdir(exist_ok=True)
    _fake_prices(path, value)
    pd.DataFrame({"date": ["2025-01-01"], "value": [domestic]}).to_csv(
        path / "domestic_cgpi.csv", index=False
    )
    return path


@pytest.fixture
def tl(monkeypatch, tmp_path):
    """trade_loss with tmp cache dir, tmp CGPI source and cheap stubbed inputs (call counter)."""
    from src.analysis import trade_loss as t

    out = tmp_path / "cache"
    src = _src_dir(tmp_path / "srcA")
    monkeypatch.setattr(t, "TRADE_LOSS_DIR", out)
    monkeypatch.setenv(ENV, str(src))
    calls = {"annual": 0, "group": 0}

    def annual(force=False):
        calls["annual"] += 1
        return pd.DataFrame(
            {"year": [2022], "group": ["energy"], "group_ja": ["x"], "price_index": [150.0]}
        )

    monkeypatch.setattr(t, "compute_annual_price_index", annual)
    monkeypatch.setattr(
        t,
        "compute_group_import_content",
        lambda force=False: pd.DataFrame({"group": ["energy"], "import_value_total": [1000.0]}),
    )
    monkeypatch.setattr(
        t, "compute_domestic_annual_index", lambda: pd.DataFrame({"year": [2022], "domestic_cgpi": [110.0]})
    )
    monkeypatch.setattr(t, "compute_group_baseline_prices", lambda: {"energy": 100.0})
    t._calls = calls
    t._out = out
    return t


def _stale_group_cache(t) -> None:
    t._out.mkdir(exist_ok=True)
    pd.DataFrame({"year": [2022], "group": ["energy"], "trade_loss_corrected_bn_jpy": [999.0]}).to_csv(
        t._out / "trade_loss_by_group.csv", index=False
    )


def test_fingerprint_tracks_content_and_env_override(monkeypatch, tmp_path):
    from src.analysis import trade_loss as t

    a = _src_dir(tmp_path / "a")
    b = _src_dir(tmp_path / "b")  # identical content
    c = _src_dir(tmp_path / "c", value=151.0)  # different import prices
    d = _src_dir(tmp_path / "d", domestic=111.0)  # different domestic CGPI
    fps = {}
    for k, p in dict(a=a, b=b, c=c, d=d).items():
        monkeypatch.setenv(ENV, str(p))
        fps[k] = t.cgpi_source_fingerprint()
    assert fps["a"] == fps["b"]
    assert len({fps["a"], fps["c"], fps["d"]}) == 3


def test_group_cache_without_stamp_is_recomputed(tl):
    _stale_group_cache(tl)
    out = tl.compute_trade_loss(force=False)
    assert out["trade_loss_corrected_bn_jpy"].iloc[0] == pytest.approx(500.0)
    assert tl._calls["annual"] == 1


def test_group_cache_with_other_vintage_stamp_is_recomputed(tl):
    _stale_group_cache(tl)
    (tl._out / "trade_loss_by_group.csv.srcsha").write_text("deadbeef")
    out = tl.compute_trade_loss(force=False)
    assert out["trade_loss_corrected_bn_jpy"].iloc[0] == pytest.approx(500.0)


def test_group_cache_with_same_vintage_is_reused_and_stamped_after_compute(tl):
    first = tl.compute_trade_loss(force=False)  # computes + stamps
    assert tl._calls["annual"] == 1
    second = tl.compute_trade_loss(force=False)  # same vintage -> cache
    assert tl._calls["annual"] == 1
    pd.testing.assert_frame_equal(first.reset_index(drop=True), second.reset_index(drop=True))


def test_group_cache_invalidated_when_source_content_changes(tl, monkeypatch, tmp_path):
    tl.compute_trade_loss(force=False)
    monkeypatch.setenv(ENV, str(_src_dir(tmp_path / "srcB", value=160.0)))
    tl.compute_trade_loss(force=False)
    assert tl._calls["annual"] == 2


def test_force_true_always_recomputes(tl):
    tl.compute_trade_loss(force=False)
    tl.compute_trade_loss(force=True)
    assert tl._calls["annual"] == 2


def test_total_cache_without_stamp_is_recomputed(tl):
    tl._out.mkdir(exist_ok=True)
    pd.DataFrame({"year": [2022], "total_corrected_bn_jpy": [999.0], "gdp_pct": [1.0]}).to_csv(
        tl._out / "trade_loss_total.csv", index=False
    )
    out = tl.compute_total_trade_loss(force=False)
    assert out["total_corrected_bn_jpy"].iloc[0] == pytest.approx(500.0)


def test_total_cache_same_vintage_reused_but_gdp_pct_refreshed(tl):
    tl.compute_total_trade_loss(force=False)  # computes + stamps
    path = tl._out / "trade_loss_total.csv"
    cached = pd.read_csv(path)
    cached["gdp_pct"] = 123.456  # stale GDP ratio left over from an older GDP table
    cached.to_csv(path, index=False)
    n = tl._calls["annual"]
    out = tl.compute_total_trade_loss(force=False)
    assert tl._calls["annual"] == n  # cache reused
    assert out["gdp_pct"].iloc[0] == pytest.approx(500.0 / 584_501.3 * 100)
