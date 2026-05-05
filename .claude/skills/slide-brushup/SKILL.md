---
name: slide-brushup
description: ゼミ発表スライドの監査と画像プロンプト初版生成。表記ミス・典拠ズレ・プレースホルダ検出 → 画像追加箇所抽出 → ChatGPT Image2 用プロンプト生成までを構造化アウトプット（brushup-plan.md）として出力する。トリガー語は "スライド監査", "ブラッシュアップ計画", "画像プロンプト用意", "slide audit", "slide brushup", "スライドの誤りチェック"。
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Slide Brushup

ゼミ発表スライドのブラッシュアップを **2 フェーズ構成** で実行する。修正の自動適用・画像の自動生成は行わず、**整理されたアウトプット（brushup-plan.md）** を生成することがスキルの責務。

**References** (always read first):
- `docs/DESIGN.md` — ビジュアル・トーン・構造の全ルール
- `.claude/slide-context.yaml` — 静的事実（人・タイトル・発表メタ・配色・画像ワークフロー）
- `docs/INDEX.md` → `docs/overview.md` / `docs/research-design.md` / `docs/decision-log.md` — 典拠の一次ソース
- `docs/literature/INDEX.md`（存在する場合）— 引用文献の正規表記

---

## Step 0: Parse Intent

ユーザー依頼から以下を抽出:
- **対象スライドファイル**: `slides/<id>-*.html` または `.md`（明示なければ最新の `slides/` 配下から推定）
- **発表ID**: `slide-context.yaml` の `presentations[*].id` と紐付け
- **重点モード**:
  - A) テキスト監査のみ
  - B) 画像計画のみ
  - C) 両方（デフォルト）

---

## Step 1: 入力読み込み（並列）

- 対象スライド本体
- `.claude/slide-context.yaml`
- `docs/DESIGN.md`
- `docs/overview.md` / `docs/research-design.md` / `docs/decision-log.md`
- `slides/assets/`（既に画像があれば Glob で把握）

---

## Phase A: テキスト監査

### A-1. プレースホルダ検出
スライド内を Grep で検索:
- `○○` / `〇〇` / `<TBD>` / `TODO` / `XXX` / `TBA` / `要確認`
- `slide-context.yaml` の `<TBD>` 値もあわせて報告（YAML 側の未充足はスライド事故の原因）

### A-2. 著者名・年次・典拠の照合
- スライド内の引用（著者・年・誌名）を抽出
- `docs/research-design.md` 参考文献節 / `docs/literature/INDEX.md` と照合
- スペル・年・誌名のズレを「typo / citation 候補」として記録

### A-3. 数値の整合性
スライド上の数値（価格上昇率・推定値・規模等）を以下と照合:
- `docs/research-design.md`（推定結果テーブル / 5グループ上昇率）
- `docs/decision-log.md`（DEC-009 / DEC-010 の β=0.194→0.431 等）
- 食い違いは「number 候補」として記録

### A-4. DESIGN.md 準拠チェック
チェック項目:
- 1スライド1メッセージ
- 箇条書き 3〜6 上限
- 配色: 主要 3色以内 / navy・blue 系統 / orange は注意点のみ
- 装飾的視覚物の有無
- フォント・整列・余白の一貫性

### A-5. 5グループの順序統一
`slide-context.yaml` の `import_groups_order` と一致するか確認。

### A-6. 進捗ステータスの一貫性
`phase_status` と スケジュール・本文の表現が乖離していないか確認（例: 「これから Phase 1」と書きつつ内部完了済の場合は注釈を出す）。

### A-7. アウトプット表

| # | スライド | 該当箇所 | 種別 | 現状 | 修正案 | 根拠 | 優先度 | 状態 |
|---|---------|---------|------|------|--------|------|--------|------|

種別: `placeholder` / `typo` / `citation` / `number` / `design` / `consistency` / `progress`
優先度: `必須` / `推奨` / `任意`

---

## Phase B: 画像追加計画

### B-1. 既存画像箇所の確認
`slides/assets/` を Glob し、既存画像をリスト化。

### B-2. 画像追加候補の抽出
各スライドを以下で評価:
- テキスト密度が高すぎ可読性を損なっていないか
- 概念図・フロー図で読みやすさが上がるか
- DESIGN.md の "Charts, Tables, and Diagrams" の **分析目的** 要件を満たすか
- ヒーロー画像・背景画像の妥当性（タイトル・章扉のみ可）

### B-3. 各画像の意図整理

| slot | スライド番号 | 意図・伝達ニュアンス | 構図 | 配置位置 | サイズ目安 | ファイル名 |
|------|------------|------------------|------|---------|-----------|-----------|

### B-4. Image2 プロンプト生成

DESIGN.md・slide-context.yaml `image_workflow.style_constraints` / `forbidden` を反映した英語プロンプトを生成。

#### プロンプト雛形

```
A clean, minimal, academic illustration for a Japanese economics thesis presentation slide.
Subject: <意図を英訳>
Composition: <構図指定>
Style: minimalist editorial illustration / line diagram. Restrained color palette: navy (#1a2e4a), blue-gray (#4a7fa5), white background only. No other colors except a single muted orange (#b85c1a) for accent if necessary.
Constraints: flat 2D, no photorealistic textures, no cartoon style, no decorative shapes, no gradients, no marketing tone, no people unless schematic.
Output: 1200x675 px, pure white background, designed to sit cleanly inside an academic slide deck. Whitespace allowed.
```

---

## Step 2: アウトプット書き出し

`slides/<id>-brushup-plan.md` に以下の構造で保存:

```markdown
# <発表ID> Brushup Plan
_Generated: YYYY-MM-DD_

対象: `<対象ファイル>`
発表日: <date>
モード: <A/B/C>

## §1. テキスト監査結果
（Phase A の表 + 補足）

## §2. 画像追加計画
（Phase B-1〜B-3 の表 + 補足）

## §3. Image2 プロンプト集
### s01 …
（プロンプト全文）

### s02 …
…

## §4. 実行順序
1. テキスト修正適用（§1 の優先度=必須から順に）
2. `slides/assets/` 作成（未作成なら）
3. Image2 で画像生成（§3 のプロンプトをコピー & 実行）
4. スライド HTML 内のプレースホルダコメントを `<img>` タグに差し替え
5. DESIGN.md "Final Check" で自己検証
```

---

## Step 3: サマリー報告

ユーザー向けに簡潔に報告:
- 検出した修正項目数（種別ごと）
- 提案した画像 slot 数
- アウトプットファイルパス
- 次のアクションの提示（修正適用 or プロンプト送付 を待つ）

---

## Scope Boundaries

このスキルは:
- **やる**: 監査結果の構造化 / 画像プロンプトの初版生成 / brushup-plan.md の出力 / 既存スライドの問題抽出
- **やらない**:
  - スライド本体の自動修正適用（ユーザーレビュー後に別ステップで実施）
  - 画像の自動生成（ChatGPT Image2 はユーザー側で実行）
  - `docs/DESIGN.md` 自体の改訂
  - `docs/` の研究内容自体の修正
  - `slide-context.yaml` の `<TBD>` 値の埋め込み（ユーザー判断）

---

## 再利用ノート

このスキルは **4 回のゼミ発表すべて** で使用する想定:
- seminar1（5/20 計画発表） — 初回チェックと画像基盤整備
- seminar2（7月 Phase 1〜2 結果） — 結果数値の典拠照合が主
- seminar3（秋 論文ドラフト全体） — 構成・章立てチェック
- seminar_final（1月末 提出前） — 最終 typo・整合性チェック

各回で `slide-context.yaml` の `presentations` を参照し、対象 ID 配下の HTML を入力にする。
