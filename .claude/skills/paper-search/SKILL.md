---
name: paper-search
description: Search academic papers on Google Scholar, CiNii, SSRN, and NBER. Use when the user asks to find papers, literature, 論文検索, 先行研究, or needs to check definitions/methodologies used in economics research.
allowed-tools: WebSearch, WebFetch, Read
---

# Paper Search

Search academic literature for the user's thesis research. Follow these steps.

**Reference:** [shared/search-guidelines.md](../shared/search-guidelines.md) — apply all shared formatting and query rules.

---

## Step 1: Understand the Search Intent

Classify what the user needs:
- **A) Topic search**: find papers on a research topic (e.g., "cost-push inflation and consumption")
- **B) Definition check**: find how a term is used in economics literature (e.g., "what does 実消費 mean in the literature")
- **C) Method search**: find papers using a specific methodology (e.g., "shift-share instrument for inflation")

This determines the query strategy.

---

## Step 2: Construct Queries

Build 2-3 search queries:
1. **English academic query** — for Google Scholar / NBER / SSRN
   - Example: `"cost-push inflation" household consumption Japan panel`
2. **Japanese academic query** — for CiNii / J-STAGE
   - Example: `コストプッシュ インフレ 家計消費 実証`
3. **(Optional) Method-specific query** — if the user needs methodology references
   - Example: `"shift-share" "import price shock" consumption`

Use `WebSearch` for each query. Target these sources:
- Google Scholar: `site:scholar.google.com` or general academic terms
- CiNii: include `site:cir.nii.ac.jp` or `CiNii` in query
- NBER/SSRN: include `site:nber.org` or `site:ssrn.com` when relevant

---

## Step 3: Filter and Rank

From raw results:
1. Remove clearly irrelevant hits
2. Prioritize: peer-reviewed > working papers > policy reports
3. Prioritize: Japan-specific > other advanced economies > general
4. Prioritize: recent (2020+) > older, unless older is seminal

---

## Step 4: Output

Present results following the shared formatting rules. Add a brief **"How this relates to your thesis"** note (1 sentence) for the top 3 results.

If the search was a **definition check (B)**, instead of a results table, provide:
- The standard academic definition with citation
- How it differs from colloquial usage (if relevant)
- Which definition is most appropriate for the user's context
