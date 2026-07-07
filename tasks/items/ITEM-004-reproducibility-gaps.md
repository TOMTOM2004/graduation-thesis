---
id: ITEM-004
title: 再現性の残穴 — shapiro e-Statキャッシュ化・GDP vintage確定・stale processed削除判断
status: todo
priority: P2
source: self
context: personal
created: 2026-07-07
updated: 2026-07-07
links: [docs/decision-log.md]
---

## 背景

DEC-019/021 の再現性強化で残った3つの穴。論文提出前に「rawから全再生成→golden一致」を第三者が再現できる状態にする。

## 現状 / next action

- [ ] `shapiro_decomp` の e-Stat 品目名をキャッシュ化（現状 API キー必須＝再現性の残穴。DEC-021 でも再実行不可と記録）
- [ ] GDP 561兆の vintage 確定（`trade_loss.py` 内 TODO。GDP比計算の分母出典を一次資料で固定）
- [ ] `data/processed_stale_20260706/` の削除判断（DEC-023 で main の data/processed は暦年再生成済み。新キャッシュ安定後に削除。**削除前にユーザー確認**）

## Decision log

