---
name: estat-search
description: Search Japan's e-Stat and other data sources for datasets, metadata, and variable availability. Use when the user asks about government statistics, e-Stat, 政府統計, データ検索, or needs to check what public data is available. Saves results to docs/data-sources/.
context: fork
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Glob
---

# e-Stat Search

Search Japan's government statistics and related data sources, assess fitness, and save results.

**Reference**: [shared/search-guidelines.md](../shared/search-guidelines.md) — query construction and formatting rules.

---

## Step 0: Parse Data Need

Classify:
- **A) Dataset discovery**: what datasets exist for a topic
- **B) Variable check**: what variables are in a specific survey
- **C) Metadata/coverage**: time range, granularity, frequency, sample size
- **D) API/download info**: how to access programmatically

Check `docs/data-sources/INDEX.md` for prior results on the same dataset.

---

## Step 1: Parallel Search

Run queries targeting:

**Group A — e-Stat portal**:
- `site:e-stat.go.jp` + topic keywords in Japanese

**Group B — Survey documentation**:
- Survey name + `調査概要` or `利用案内` or `総務省`

**Group C — Related sources** (when relevant):
- BOJ: `site:boj.or.jp 統計`
- Cabinet Office: `site:cao.go.jp` (GDP/SNA)
- METI: `site:meti.go.jp` (commercial statistics)
- RIETI: `site:rieti.go.jp` (research data)

Use `WebFetch` to read specific pages for metadata when needed.

---

## Step 2: Assess Fitness

For each dataset, evaluate:

| 項目 | 内容 |
|------|------|
| Geographic granularity | national / prefectural / municipal |
| Time granularity | annual / quarterly / monthly |
| Time range | start — latest available |
| Key variables | breakdowns available |
| Sample size / coverage | survey-based or census-based |
| Access method | API / CSV / application required |
| Known limitations | sample size, coverage gaps, revision frequency |

---

## Step 3: Preview and Save

Present fitness assessment to the user. Then save:

1. **Dataset entry**: Append to `docs/data-sources/INDEX.md` under the appropriate section (公的統計 or オルタナティブデータ)

Format per dataset:
```markdown
### [Survey Name]（Source Organization）
- **粒度**: prefecture × monthly × category
- **期間**: 2015-01 — 2026-02
- **主要変数**: ...
- **アクセス**: API / CSV download
- **適合度**: Phase 1 の都道府県×月次×カテゴリ分析に [適合/一部適合/不適合]
- **制約**: ...
- **調査日**: 2026-04-10
```

---

## Key Surveys Reference

For household consumption research, check these first:
- **家計調査** (Family Income and Expenditure Survey) — 総務省
- **全国家計構造調査** (National Survey of Family Income and Expenditure) — 総務省
- **家計消費状況調査** (Survey of Household Economy) — 総務省
- **消費者物価指数** (CPI) — 総務省
- **国民経済計算** (SNA/GDP) — 内閣府
- **商業動態統計** (Commercial Statistics) — 経産省

---

## Scope Boundaries

This skill does **NOT**:
- Download actual datasets
- Write data cleaning code
- Perform data quality assessment beyond metadata review
