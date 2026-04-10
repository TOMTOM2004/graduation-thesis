---
name: literature-review
description: Synthesize saved paper summaries into a literature review. Use when the user asks to organize, synthesize, compare papers, identify research gaps, or position their thesis contribution. Requires papers already saved via paper-search.
context: fork
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Literature Review

Synthesize saved paper summaries into structured analysis. This skill works on papers already saved in `docs/literature/papers/` by `paper-search`.

---

## Step 0: Check Prerequisites

Read `docs/literature/papers/` directory. If fewer than 3 papers exist, warn:
> 「論文が3件未満です。先に /paper-search で論文を追加してください。」

Read `docs/literature/matrix.md` for the current comparison matrix.

---

## Step 1: Classify Request

- **A) Matrix update**: Refresh or fill gaps in the comparison matrix
- **B) Gap analysis**: Identify what's missing in the literature coverage
- **C) Synthesis**: Write a structured literature review section
- **D) Positioning**: Articulate this thesis's contribution relative to existing work

---

## Step 2: Execute

### For Gap Analysis (B)

1. Read all paper summaries in `docs/literature/papers/`
2. Cross-reference with the category tags in `docs/literature/INDEX.md`
3. Report:

```
## カバレッジ状況

| カテゴリ | 論文数 | カバレッジ | 備考 |
|---------|--------|-----------|------|
| cost-push-inflation | 3 | ○ | 日本事例が不足 |
| identification-strategy | 0 | ✗ | 要追加 |
```

4. Suggest specific search queries to fill gaps

### For Synthesis (C)

1. Read all paper summaries
2. Organize by theme (not chronologically)
3. For each theme:
   - What is the consensus?
   - Where do papers disagree?
   - What remains unanswered?
4. Write to `docs/literature/review-draft.md`

### For Positioning (D)

1. Read all paper summaries + `docs/overview.md` (this thesis's research question)
2. Identify:
   - What existing papers have already done
   - What this thesis does differently (data, method, scope, question)
   - The specific gap this thesis fills
3. Write a concise positioning statement (3-5 sentences)

---

## Step 3: Save

- Update `docs/literature/matrix.md` if changed
- Save synthesis to `docs/literature/review-draft.md`
- Save positioning to `docs/literature/positioning.md`

---

## Scope Boundaries

This skill does **NOT**:
- Search for new papers (use `paper-search`)
- Write final thesis prose (this produces structured drafts)
- Evaluate paper methodology quality
