---
id: ITEM-003
title: ハンドオフ§8 残り — 現代 event study/DID（小麦補強）③・財政乗数の状態依存④
status: todo
priority: P3
source: self
context: personal
created: 2026-07-07
updated: 2026-07-07
links: [tasks/先行研究_識別戦略ハンドオフ_20260707.md, docs/decision-log.md]
---

## 背景

先行研究ハンドオフ（2026-07-07）の優先①②は DEC-024 で消化済み。残る③④は本丸でないため分離。引用は DEC-024 で原典 verify 済みなので調査は中身の精読から入れる。

## 現状 / next action

- **③ 現代 event study/DID の負の重み是正**: ウクライナ小麦イベントスタディ（KEEP・ITS 実装済み）の頑健性語彙の補強用。Callaway & Sant'Anna 2021 (J.Econom 225(2) 200-230) / Sun & Abraham 2021 (同 175-199) / de Chaisemartin & D'Haultfœuille 2020 (AER 110(9) 2964-2996) / Borusyak, Jaravel & Spiess 2024 (REStud 91(6) 3253-3285)。※本研究の ITS は単一処置系列＝staggered 設計でないため負の重み問題は直接は効かない見込み→「なぜ本設計では問題にならないか」を1段落書ければ十分の可能性が高い（過剰実装しない）
- **④ 財政乗数の状態依存**: Auerbach & Gorodnichenko 2012 / DeLong & Summers 2012。政策シナリオ章（policy_comparison）を理論で裏打ちしたい場合**のみ**。Phase 3 は定性・例示に降格済み（DEC-014）なので優先度低のまま
- Next: 論文の考察・限界章の執筆時（[[ITEM-002]]）に③の要否を判断してから着手

## Decision log

- 2026-07-07: DEC-024 のスコープから明示的に除外して分離
