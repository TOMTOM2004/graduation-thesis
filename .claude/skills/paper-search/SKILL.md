---
name: paper-search
description: Search academic papers and save structured summaries. Use when the user asks to find papers, literature, 論文検索, 先行研究, or needs to check definitions/methodologies. Saves results to docs/literature/.
context: fork
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Glob, Grep
---

# Paper Search

Search academic literature, verify results, and save structured summaries.

**References** (read when needed):
- [shared/search-guidelines.md](../shared/search-guidelines.md) — query construction, formatting, verification rules
- [shared/paper-summary-template.md](../shared/paper-summary-template.md) — output format and category tags

---

## Step 0: Parse Intent

From the user's request, extract:
- **Topic keywords**: what to search for
- **Intent type**: A) topic search, B) definition check, C) method search, D) specific paper lookup
- **Scope constraint**: if the user specified a particular aspect (e.g., "日本の事例のみ")

Check `docs/literature/search-log.md` for prior searches on the same topic. If a similar search was already run, inform the user and ask whether to expand or skip.

---

## Step 1: Parallel Search Groups

Run 2-3 WebSearch queries **in parallel**:

**Group A — English academic**:
- Target: Google Scholar, NBER, SSRN, RePEc
- Query pattern: `"cost-push inflation" household consumption Japan panel`

**Group B — Japanese academic**:
- Target: CiNii, J-STAGE, 経済産業研究所(RIETI)
- Query pattern: `コストプッシュ インフレ 家計消費 実証`

**Group C — Methodology** (if relevant):
- Target: methodology-specific searches
- Query pattern: `"shift-share" "import price" consumption heterogeneity`

---

## Step 2: Filter and Classify

From raw results:

1. **Verify existence**: Each paper must appear in search results. If not verifiable, mark `【未検証】`
2. **Remove** clearly irrelevant hits
3. **Classify importance**:
   - **High**: Directly addresses this thesis's question, similar methodology or data, Japan-focused
   - **Medium**: Related topic/method, partially applicable
   - **Low**: Tangential, background only
4. **Rank**: High first, then by recency (2020+ preferred unless seminal)

---

## Step 3: Preview Results

Present a summary table to the user:

```
| # | 著者 | 年 | タイトル | 手法 | 重要度 | 本研究との関連 |
|---|------|-----|---------|------|--------|---------------|
```

For **definition checks** (Intent B), instead provide:
- Standard academic definition with citation
- Colloquial vs academic usage differences
- Recommended usage for this thesis

Ask: 「保存する論文を選んでください（番号指定 or 全部）」

---

## Step 4: Save

For each selected paper:

1. **Paper summary file**: Save to `docs/literature/papers/<author>-<year>-<keyword>.md` using the template from `shared/paper-summary-template.md`
   - Assign sequential ID (P001, P002, ...)
   - Check existing IDs in `docs/literature/papers/` to avoid collision

2. **Matrix update**: Append a row to `docs/literature/matrix.md`

3. **INDEX update**: Add entry under the appropriate category in `docs/literature/INDEX.md`

4. **Search log**: Append to `docs/literature/search-log.md`:
   ```
   | 日付 | クエリ | ソース | ヒット数 | 追加論文数 | 備考 |
   ```

---

## Step 5: Gap Report

After saving, briefly assess:
- Which categories in `docs/literature/INDEX.md` are still empty?
- Are there obvious gaps in coverage (e.g., no Japan-specific papers, no methodology references)?
- Suggest 1-2 follow-up search queries to fill gaps

---

## Scope Boundaries

This skill does **NOT**:
- Write literature review prose (use `literature-review` for synthesis)
- Download PDFs or full texts
- Generate BibTeX (future enhancement)
- Evaluate paper quality beyond importance classification
