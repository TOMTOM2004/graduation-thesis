# BOJ CGPI source vintage 2026-10-13 (ITEM-025 / D2・D3)

Immutable once written. `data/raw/boj-cgpi/` (earlier snapshot, 2026-03 vintage) is untouched; this directory is a parallel,
versioned copy selected explicitly via `CGPI_SOURCE_DIR`.

| item | value |
|---|---|
| publisher | Bank of Japan, 企業物価指数 (CGPI) 2020年基準 |
| zip URL | https://www.stat-search.boj.or.jp/info/cgpi_m_jp.zip |
| zip Last-Modified | Tue, 13 Oct 2026 00:35:39 GMT (data through 2026-09) |
| link CSV URL | https://www.stat-search.boj.or.jp/info/cgpilink1.csv |
| link CSV Last-Modified | Fri, 22 Apr 2022 01:11:26 GMT (identical to data/raw copy) |
| retrieved | 2026-10-22 11:36 UTC (20:36 JST) by the ITEM-025 freshness audit; copied byte-for-byte from `/private/tmp/ic-fresh-20261022/boj/` |
| response headers | `response-headers-*.txt` (verbatim) |

## SHA-256

Source (official, byte-exact):

| file | bytes | sha256 |
|---|---:|---|
| cgpi_m_jp.zip | 342423 | `7ad65cba26372fef88401390ce7f4055afae0fea1f6d0479a64e7738a98a1a43` |
| cgpilink1.csv | 333873 | `cf38d934941925c001fbdf55f6f659c03b10699155a1bf8ba89e29fd9400f4e1` |

Derived (regenerable, do not hand-edit): see `SHA256SUMS` for the current hashes of
`import_prices_extracted.csv` and `domestic_cgpi.csv`.

Superseded snapshot for comparison (`data/raw/boj-cgpi/cgpi_m_jp.zip`):
`a7ac74aacac232e36d076891384aacccc6550a91ca7602af8ff00b21ecf33273`.

## Regeneration of derived files

```
CGPI_SOURCE_DIR=$PWD/data/source-vintages/boj-cgpi-20261013 \
  .venv/bin/python -c "from src.data.fetch_import_prices import extract_import_prices, extract_domestic_cgpi as d; extract_import_prices(); d()"
```
(zip + link CSV only; same code path as the default, 2015–2019 from link CSV, 2020+ from zip.)

## Use

Set `CGPI_SOURCE_DIR` to this directory's absolute path. Unset = historical `data/raw/boj-cgpi` behaviour.
Under the override the loaders never download (a missing source file raises `FileNotFoundError`).

## Known content differences vs the data/raw snapshot (imports, 11 groups)

- 2025-01..12 revised (BOJ routine retroactive correction, 2026-09-11) and 2026-01..03 revised (preliminary → revised).
- 2026-04..09 are new months (incomplete year: excluded by the `<12 months` annual guard).
- 2015–2024 unchanged.
