# TODO — 卒業論文（案B）

_Last updated: 2026-05-03 00:22 / session: seminar1 スライド整備（A〜D 拡張・emphasis 色追加・文献正規化・Final Check）完了_

## 🎯 Next action
- What: 5/20 ゼミ発表前のリハーサル（実機 1200×675 で全 14 枚通し確認）
- Where: `slides/20260520-seminar1-proposal.html`
- Done when: 各スライドの可読性・画像コントラスト・視線フローを目視確認、必要なら微調整

## 📍 State snapshot
- ✅ Done（今セッション）:
  - slide-brushup スキル作成 + slide-context.yaml
  - seminar1 deck を 14 枚構成に拡張（s1b Hook / s10b Contribution / s3 chart / s6 venn）
  - 7 画像生成・差し込み（日本語ラベル版）
  - DESIGN.md 原則拡張（emphasis 色 / Hook / Feasibility / Contribution / Pacing / Whitespace / Page Indicator）
  - docs/feasibility.md / docs/contribution.md 新規
  - 文献正規化（s12 References 12 件・docs/literature/ と完全照合）
  - DESIGN.md Final Check 全 7 項目 PASS
- 🟡 In progress: なし
- 🔴 Blocked: なし

## 🧠 Context not in code
- 進捗判断: s11 Schedule は計画形維持（第1回は "まだやってない体" で口頭補足する戦略）
- emphasis 色 muted crimson `#b03050` を新規追加（caution=orange と役割分離）
- 第1回で Feasibility は出さない方針（seminar2 用に `docs/feasibility.md` 温存）
- 任意未対応: #6 s10 の貿易統計（概況品別国別表）追加 — 第1回は省略

## ❌ Don't do (this task)
- [trap] 学術スライドの第1回（テーマ・計画）で Feasibility や結果数値を出すと、第2回・第3回の議論を先取りして発表の意義が薄れる
- [trap] DESIGN.md「余白で grouping」を機械的に中央寄せに適用すると、grouping を split して視線フローを破壊する（tail whitespace は OK / mid-flow whitespace は NG）
- [mistake] HTML Edit 時、全角括弧（）と半角() の混在で old_string がマッチしない。不確実なら Read してからコピーするか、bash sed で範囲削除を使う
- [mistake] ChatGPT Image2 の日本語ラベル指定で「Noto Sans JP / Hiragino Sans 風」「ラベルは exactly as specified」「garbled/fake-looking kanji 禁止」を明示しないと崩れる

## ❓ Open questions for user
- [ ] #6 s10 任意（貿易統計追加）は省略確定？

## 📂 Key files
- `slides/20260520-seminar1-proposal.html`
- `slides/seminar1-brushup-plan.md`
- `docs/DESIGN.md`
- `docs/feasibility.md` / `docs/contribution.md`
- `.claude/slide-context.yaml`
- `.claude/skills/slide-brushup/SKILL.md`

## ❌ Out of scope（今セッション）
- seminar2/3/final 用スライドの作成（時期到来時に slide-brushup スキルで反復）
- s11 Schedule の構造変更（計画形維持確定）

---

## 残タスク

### 執筆前準備
- [ ] 非線形モデルの扱いを明確化（research-design.md に「線形・非線形を比較」と記載。結果は線形のみ → 非線形を試した結果を記録するか、未実施の理由を DEC に追記）
- [ ] Koyck δ=0.55 の選定根拠を文書化（DEC-011 として decision-log.md に追記。先行研究由来 / データ駆動 / 感度分析ベースのいずれかを明記）
- [ ] 先行研究との数値比較表を作成（β=0.431 vs Yagi et al. / Amiti-Itskhoki-Konings、交易損失 34.6 兆円 vs 齊藤 2022 / 内閣府推計。ロバストネス appendix 用）
- [ ] 政策シナリオ選定の透明性確保（なぜエネルギー・食料補助であり、賃金補助・産業政策ではないのかをスコープ限定として論文内で明記）

### スライド（任意・5/20 直前）
- [ ] s10 に貿易統計（概況品別国別表）を追加（任意・第1回は省略）
- [ ] 実機 1200×675 で全 14 枚リハーサル

### 論文執筆
- [ ] 先行研究レビューの執筆
- [ ] 方法論の執筆
- [ ] 結果の記述
- [ ] 考察・政策含意の執筆
- [ ] 図表の整備
- [ ] 指導教員フィードバック対応
