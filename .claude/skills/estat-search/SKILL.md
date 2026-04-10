---
name: estat-search
description: Search Japan's e-Stat (政府統計) for datasets, metadata, and variable availability. Use when the user asks about government statistics, e-Stat, 政府統計, データ検索, or needs to check what public data is available for their analysis.
allowed-tools: WebSearch, WebFetch, Read
---

# e-Stat Search

Search Japan's government statistics portal and related data sources. Follow these steps.

**Reference:** [shared/search-guidelines.md](../shared/search-guidelines.md) — apply all shared formatting and query rules.

---

## Step 1: Understand the Data Need

Classify what the user needs:
- **A) Dataset discovery**: what datasets exist for a topic (e.g., "household consumption by prefecture")
- **B) Variable check**: what variables are available in a specific survey (e.g., "what categories does 家計調査 break down into")
- **C) Metadata/coverage**: time range, geographic granularity, frequency, sample size
- **D) API/download info**: how to access the data programmatically

---

## Step 2: Construct Queries

Build queries targeting these sources:
1. **e-Stat portal**: `site:e-stat.go.jp` + topic keywords in Japanese
   - Example: `site:e-stat.go.jp 家計調査 都道府県 月次`
2. **Survey documentation**: survey name + 調査概要 or 利用案内
   - Example: `家計調査 調査概要 総務省`
3. **Related sources** (when relevant):
   - BOJ statistics: `site:boj.or.jp 統計`
   - Cabinet Office: `site:cao.go.jp` for GDP/consumption accounts
   - METI: `site:meti.go.jp` for industrial/commercial statistics

Use `WebSearch` for queries. Use `WebFetch` to read specific e-Stat pages for metadata when needed.

---

## Step 3: Assess Data Fitness

For each dataset found, evaluate:
- **Geographic granularity**: national / prefectural / municipal
- **Time granularity**: annual / quarterly / monthly
- **Time range**: start year — latest available
- **Key variables**: what breakdowns are available
- **Sample size / coverage**: survey-based or census-based
- **Access**: API available? CSV download? Requires application?

---

## Step 4: Output

Present as a structured table:

| Survey | Granularity | Frequency | Range | Key Variables | Access |
|--------|------------|-----------|-------|---------------|--------|

Add a **fitness assessment** (1-2 sentences): how well each dataset matches the user's research needs, and any known limitations (e.g., sample size too small for prefectural breakdown).

### Key Surveys to Know

For household consumption research, these are the primary candidates:
- **家計調査** (Family Income and Expenditure Survey) — 総務省
- **全国家計構造調査** (National Survey of Family Income and Expenditure) — 総務省
- **家計消費状況調査** (Survey of Household Economy) — 総務省
- **消費者物価指数** (CPI) — 総務省
- **国民経済計算** (SNA/GDP) — 内閣府
- **商業動態統計** (Commercial Statistics) — 経産省
