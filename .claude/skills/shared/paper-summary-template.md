# Paper Summary Template

Individual paper summaries saved to `docs/literature/papers/` must follow this format:

```markdown
---
id: P001
title: "Paper Title"
authors: "Author1, Author2"
year: 2024
source: "Journal Name / Working Paper Series"
doi: "10.xxxx/xxxxx"  # if available
importance: High / Medium / Low
categories:
  - cost-push-inflation
  - household-consumption
verified: true / false
added: 2026-04-10
---

## Summary
1-3 sentences on what this paper does.

## Methodology
- Identification strategy / estimation method
- Data used (source, granularity, period)

## Key Findings
- Bullet points of main results

## Relevance to This Thesis
- Which sub-question (副問1/2/3) does this relate to?
- What can we learn or adopt from this paper?
- How does our approach differ?

## Limitations / Notes
- Any caveats, data limitations, or scope differences
```

## Category Tags (use in frontmatter)
- `cost-push-inflation`: コストプッシュインフレ関連
- `household-consumption`: 家計消費分析
- `price-elasticity`: 価格弾力性・カテゴリ別分析
- `regional-heterogeneity`: 地域間異質性
- `simulation-model`: シミュレーションモデル・政策評価
- `alternative-data`: オルタナティブデータ
- `identification-strategy`: 識別戦略・手法（DID, IV, shift-share等）
- `japan`: 日本を対象とした研究
