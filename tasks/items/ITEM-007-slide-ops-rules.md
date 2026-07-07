---
id: ITEM-007
title: スライド運用ルールの策定（命名規則・格納構成・凍結方針の規約化）
status: todo
priority: P3
source: self
context: personal
created: 2026-07-07
updated: 2026-07-07
links: [docs/DESIGN.md]
---

## 背景

`slides/` に HTML 直置きで命名規則・格納が未定。凍結方針（発表済み=凍結、例: seminar1 の 34.6兆 hook は提示記録として保持）は運用実績があるが規約として未文書化。

## 現状 / next action

- 決めること: ①命名規則（`YYYYMMDD-<発表名>.html`・版管理）②格納構成（回ごとサブディレクトリ／assets 配置）③proposal.html・script.md・brushup-plan.md の対応関係 ④発表済みスライドの凍結方針の明文化（第1回は check_slides.py hook が編集時エラーを出す仕様＝実質凍結済み）
- 規約は `docs/DESIGN.md` か `.claude/slide-context.yaml` に記録
- 実害が出ていないため P3。第3回発表準備の際に併せて片付けるのが効率的

## Decision log

