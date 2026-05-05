# seminar1 Brushup Plan
_Generated: 2026-05-02_

- 対象: `slides/20260520-seminar1-proposal.html`（12 スライド）
- 発表日: 2026-05-20
- モード: C（テキスト監査 + 画像計画）
- 参照: `docs/DESIGN.md` / `.claude/slide-context.yaml` / `docs/overview.md` / `docs/research-design.md` / `docs/decision-log.md`

---

## §1. テキスト監査結果

### 1-A. 必須修正（プレースホルダ・明確な誤り）

| # | スライド | 該当箇所 | 種別 | 現状 | 修正案 | 根拠 | 状態 |
|---|---------|---------|------|------|--------|------|------|
| 1 | s1 Title | `.meta` 内 | placeholder | `○○大学経済学部` | `slide-context.yaml` の `author.affiliation` を実値で埋めて反映 | YAML 静的事実 | ✅ 対応済（専修大学経済学部） |
| 2 | s1 Title | `.meta` 内 | placeholder | `2026年5月` | `2026年5月20日` または `2026年5月20日 第1回ゼミ` 等、発表日まで明記 | プレゼン日付の精緻化 | ✅ 対応済（2026年5月20日） |
| 3 | YAML | `author.affiliation` | placeholder | `<TBD>` | 大学・学部名を実値で記入 | スライドへの反映の前提 | ✅ 対応済（専修大学経済学部） |

### 1-B. 推奨修正（精度・整合性）

| # | スライド | 該当箇所 | 種別 | 現状 | 修正案 | 根拠 | 状態 |
|---|---------|---------|------|------|--------|------|------|
| 4 | s3 Background 2 | 表エネルギー行「2020→2022年 価格上昇率」 | number | `+200% 超` | `+213〜286%`（research-design.md 表記に揃える） | research-design.md "輸入価格ショックの5グループ" | ✅ 対応済 |
| 5 | s3 Background 2 | 出所注釈 | citation | `日銀CGPI輸入物価指数（2020年基準）` | `日本銀行 企業物価指数 (CGPI) 輸入物価指数（2020年基準）。2015-2019 は連結指数 (cgpilink1.csv) を使用` | research-design.md データ制約注記 | ✅ 対応済 |
| 6 | s10 Data | テーブル | citation | データソース 5 件のみ | 識別戦略の根拠データである **貿易統計（概況品別国別表、e-Stat）** を 1 行追加可（衣料・履物の競争的輸入の根拠）。発表時間が短ければ省略可（任意） | research-design.md データ表 | ⏸ 保留（任意・第1回は省略） |
| 7 | s10 Data | 期間注記 | consistency | `分析期間: プラセボ期（2015-2019）/ ショック期（2021-2024）` | `2020 は基準年として除外（CGPI 識別力なし）` の一文を追加 | DEC-009 / overview.md スコープ節 | ✅ 対応済 |
| 8 | s11 Schedule | 第2回・第3回ゼミの日付 | consistency | `2026年7月` `2026年秋` | 月特定なら `2026年7月（仮）` 等で予定であることを明示 | 表記の正確性 | ✅ 対応済 |
| 9 | s5 Prior Research | 末尾 note | consistency | `現在調査継続中。上記は主要な参照先として暫定整理。` | 文献が `docs/literature/` で確定済なら `主要参照先（詳細は References 参照）` 等に更新 / 追加調査中なら現状維持 | 文献整備状況に依存 | ✅ 対応済（76 件整備済を反映） |

### 1-C. 任意修正（DESIGN.md 準拠 / 表現の磨き）

| # | スライド | 該当箇所 | 種別 | 現状 | 修正案 | 根拠 | 状態 |
|---|---------|---------|------|------|--------|------|------|
| 10 | s12 References | サブタイトル `主要参考文献（調査中）` | design | `（調査中）` | `（調査中）` を削除 | 1-B #9 と連動 | ✅ 対応済 |
| 11 | s12 References | Sasaki et al. (2022) 誌名 | citation | `Sasaki, H. ... Pass-through ... BOJ WP` | 著者頭文字 Y + 正式タイトル + JIMF, 123 | `papers/sasaki-yoshida-otsubo-2022-erpt-japan.md` | ✅ 対応済 |
| 12 | s12 References | Sato (2024) 誌名 | citation | `Sato, H. ... Industrial hollowing-out ... Asian Economic Policy Review` | s5/s12 から削除（B 採用：文脈ミスマッチ → Sato 2024 は経常収支論文） | `papers/sato-2024-current-account-fiscal.md` 文脈不一致 | ✅ 対応済（削除） |
| 13 | s12 References | Miwa (2024) 誌名 | citation | `Miwa, K. ... income balance ... Journal of Japanese Economy` | 著者頭文字 T + 正式タイトル + Nomura Foundation | `papers/miwa-2024-japan-bop-issues-impact.md` | ✅ 対応済 |
| 14 | s12 References | O'Donoghue et al. (2025) 誌名 | citation | `O'Donoghue ... IO price models ... Journal of Policy Analysis` | 正式タイトル「The Distributional Impact of Inflation in Pakistan: A Case Study of PRICES」 + IJM, 18(1) | `papers/odonoghue-etal-2025-distributional-inflation-pakistan-prices.md` | ✅ 対応済 |
| ＋ | s12 References | Yagi 年・誌名 | citation | `Yagi (2023) ... Japanese Economic Review` | 年 2022 + Bank of Japan Working Paper（s5/s12 両方）| `papers/yagi-2022-pass-through.md` | ✅ 対応済 |
| ＋ | s12 References | Kohli (2004, 2023) | citation | 1 行に 2 論文混在 | 2 論文に分離: 2004=JIE 62(1)・2023=RoIW 69(4) | P052/P053 別論文 | ✅ 対応済 |
| ＋ | s12 References | Minton & Somale (2025) | citation | `Import exposure ... REStat` | 正式タイトル「Detecting Tariff Effects on Consumer Prices in Real Time」+ FEDS Notes | P070 ファイル | ✅ 対応済 |
| ＋ | s12 References | Thorbecke (2024) | citation | 二論文区別なし `Japan's manufacturing trade structure ... RIETI DP` | P035 機械輸出論文に特定: 「Investigating Japan's Machinery and Equipment Exports after the GFC」 RIETI DP 24-E-033 | P034/P035 区別 | ✅ 対応済 |
| ＋ | s12 References | 齊藤 (2022) | citation | `「交易損失とGNI：日本経済の所得流出構造」、有斐閣` | 正式タイトル「交易条件の悪化と賃上げ」+ 日本経済研究センター コラム | P030 ファイル | ✅ 対応済 |
| ＋ | s12 References | Amores et al. (2025) | citation | `Inflation and income inequality ... ECB Working Paper` | 正式タイトル + Review of Income and Wealth, 71, e12713 | P076 ファイル | ✅ 対応済 |

### 1-D. 進捗表現の一貫性チェック（要ユーザー判断）

| # | スライド | 該当箇所 | 種別 | 現状 | コメント |
|---|---------|---------|------|------|---------|
| 15 | s11 Schedule | 「2026年6月 Phase 1」「7月 Phase 2」「8〜10月 Phase 3」 | progress | 未来形のスケジュール | 内部的には Phase 1〜3 完了済（CLAUDE.md / `slide-context.yaml`）。**第1回ゼミは "計画発表" 体裁** として未来形のままで問題ないが、指導教員へ「実際は予備分析が進んでおり、6月以降は精緻化フェーズ」と口頭補足する想定で良いか確認推奨 |
| 16 | s9 Framework Phase 2 | `費目別の価格転嫁率を推定（パネルOLS）` | progress | 計画形 | 既に β=0.431 (p=0.002) のメイン仕様が確定済み（DEC-010）。第1回スライドでは結果に踏み込まない方針なら現状維持で OK |

### 1-E. 監査サマリー（最終）

- 検出種別: placeholder=2 / citation=10 / number=1 / consistency=3 / design=1 / progress=2
- **必須対応**: 3 件 → ✅ **3 / 3 完了**
- **推奨対応**: 6 件 → ✅ **5 / 6 完了**（#6 のみ任意省略：第1回は時間制約で見送り）
- **任意修正**: #10〜#14 + 追加発見 6 件（Yagi 年 / Kohli 分離 / Minton 誌名 / Thorbecke 特定 / 齊藤 タイトル / Amores 詳細） → ✅ **全対応済**（`docs/literature/` 76 件と完全照合）
- **進捗判断**: #15 計画形維持（A 採用）/ #16 実質解消済 → ✅ **判断完了**

---

## §2. 画像追加計画

### 2-A. 既存画像の状況
- `slides/assets/` ディレクトリ作成済 ✅
- 全 7 画像（s01 / s02 / s03 / s04 / s06 / s08 / s09）配置 + HTML 差し込み済 ✅
- 日本語ラベル版で全画像再生成・規約名にリネーム済

### 2-B. 画像追加 slot 一覧（最終: 7 slot）

| slot | スライド | 意図・伝達ニュアンス | ファイル名 | 状態 |
|------|---------|------------------|-----------|------|
| s01 | s1 Title | 貿易フロー（モノ・カネの国際的な流れ）の薄いビジュアル背景 | `s01-title-bg.png` | ✅ 適用済（CSS background-image） |
| s02 | s2 Background 1 | 1990年代以降の構造変化 3段階概念図（製造業海外移転 → 輸入依存 → 所得流出） | `s02-structural-shift.png` | ✅ 適用済 |
| **s03** | s3 Background 2 | 5 グループ別 輸入物価指数の時系列折れ線（2020-2024、エネルギー強調） | `s03-import-price-timeseries.png` | ✅ 適用済（D で追加。table+chart 2 カラム） |
| s04 | s4 Problem Setting | コストプッシュ vs デマンドプルの識別メカニズム 2 散布図 | `s04-identification-mechanism.png` | ✅ 適用済 |
| s06 | s6 Research Gap | 3 空白の重なりベン図 | `s06-gap-venn.png` | ✅ 適用済（任意 → 採用、レイアウト 2カラム化） |
| s08 | s8 Hypothesis | 所得五分位 × 必需品支出割合 × 輸入価格ショック影響の二軸チャート | `s08-engel-import-shock.png` | ✅ 適用済 |
| s09 | s9 Framework | Phase 1〜3 のデータフロー統合図（入力→処理→出力） | `s09-framework-overview.png` | ✅ 適用済（旧 `.flow` テキスト 3 ボックスは削除し画像中心に変更） |

### 2-C. DESIGN.md・YAML 整合性チェック
全画像で以下を保証する設計:
- 配色: navy (`#1a2e4a`) / blue-soft (`#4a7fa5`) / white を主、orange は例外的アクセントのみ
- スタイル: clean / minimal / academic / calm / no decoration
- 禁止: photorealistic / cartoon / gradients / 3D / marketing tone

---

## §3. Image2 プロンプト集（日本語ラベル版）

> **使用方法**: 各セクションのプロンプト全文をコピーし、ChatGPT (Image2 / GPT Image) にそのまま投入する。生成後 `slides/assets/<filename>` に保存。
>
> **重要**: 日本語ラベルは画像生成 AI が崩しやすい。生成後に必ず文字を確認し、おかしければ「Regenerate keeping the exact Japanese labels: …」のように再生成依頼を行う。崩れる場合は短い言葉に置き換える（例: 「製造業の海外移転」→「海外移転」）。

### s01 — Title Background

> 文字なし背景画像なので英語版とほぼ同一（変更不要）。

```
A clean, minimal, academic illustration intended as a faint background layer for the title slide of a Japanese economics thesis presentation.

Subject: an extremely abstract, faint visualization of international trade flow — a stylized world arc with thin connecting lines and small directional arrows suggesting goods and capital moving between regions, hinting at Japan in the East and trading partners across the globe. Symbolic only; no realistic geography.

Style: minimalist editorial line art. Restrained color palette using navy (#1a2e4a) and blue-gray (#4a7fa5) as faint strokes on a pure white background. Strokes should be thin (1–1.5px), low opacity (around 15–25%), so that dark title text overlaid on top remains fully readable.

Composition: lots of negative space, lines distributed toward the edges, central area mostly empty for title text overlay. Horizontal arrangement.

Constraints: flat 2D, no photorealistic textures, no cartoon style, no decorative shapes, no gradients, no people, no marketing tone, no bright colors. NO text or characters of any language in the image.

Output: 1200×675 px, pure white background, designed to sit beneath title typography in an academic slide deck.
```

### s02 — Structural Shift（製造業の海外移転 → 輸入依存 → 所得の海外流出）

```
A clean, minimal, academic 3-step concept diagram for a Japanese economics thesis slide explaining structural change since the 1990s. All labels MUST be in Japanese, rendered exactly as specified below using clean Japanese sans-serif typography (Noto Sans JP / Hiragino Sans style). Do not translate or romanize the labels.

Subject: three sequential stages arranged left to right.
  Stage 1 — header label: 「製造業の海外移転」 — a small factory icon moves from a Japan-shaped silhouette toward an overseas region.
  Stage 2 — header label: 「輸入依存」 — arrows showing goods flowing back into Japan.
  Stage 3 — header label: 「所得の海外流出」 — arrows showing money flowing out of Japan to overseas.

Above each stage put a small numbered circle (1, 2, 3) — circles 1 and 2 in navy, circle 3 in muted orange to signal the problem.

Style: minimalist line / flat icon diagram. Restrained palette: navy (#1a2e4a) for outlines, blue-gray (#4a7fa5) for arrows and secondary elements, white background. A single muted orange (#b85c1a) may be used only on stage 3.

Composition: three equal-width panels, connected by short horizontal arrows or dashed dividers. Generous whitespace.

Constraints: flat 2D, no photorealistic textures, no cartoon style, no shadows or gradients, no decorative shapes, no marketing tone. Iconography must be schematic, not illustrative. Japanese characters MUST be rendered cleanly and accurately — do not produce garbled or fake-looking kanji.

Output: 1100×400 px, pure white background.
```

### s04 — Identification Mechanism（コストプッシュ vs デマンドプル）

```
A clean, minimal, academic side-by-side conceptual diagram for a Japanese economics thesis slide illustrating an identification strategy. All labels MUST be in Japanese, rendered exactly as specified below using clean Japanese sans-serif typography (Noto Sans JP / Hiragino Sans style). Do not translate or romanize the labels.

Subject: two small scatter-plot concepts side by side.
  Left panel — title: 「コストプッシュ」 — horizontal axis label: 「輸入含有率（低 → 高）」, vertical axis label: 「価格上昇率（低 → 高）」. Points form a clear upward-sloping pattern, indicating positive correlation.
  Right panel — title: 「デマンドプル」 — same axes (with the same Japanese labels), but points are scattered horizontally near a flat line, indicating no relationship to import content ratio.

Axis tick labels are simple Japanese: 「低」「高」 only.

Style: minimalist line chart. Navy (#1a2e4a) axes and labels, blue-gray (#4a7fa5) data points (small filled circles, around 8 points each). White background. Panel titles directly above each panel in small navy text.

Composition: two equal-width panels with consistent axes. No grid clutter, only minimal tick marks.

Constraints: flat 2D, schematic only (not real data), no photorealistic textures, no gradients, no 3D, no decorative shapes, no marketing tone. Japanese characters MUST be rendered cleanly and accurately — do not produce garbled or fake-looking kanji.

Output: 1100×320 px, pure white background.
```

### s08 — Engel's Law × Import Price Shock（所得階層別の異質な影響）

```
A clean, minimal, academic dual-axis chart concept for a Japanese economics thesis slide illustrating heterogeneous impact across income quintiles. All labels MUST be in Japanese, rendered exactly as specified below using clean Japanese sans-serif typography (Noto Sans JP / Hiragino Sans style). Do not translate or romanize the labels.

Subject: a single chart with horizontal axis label: 「所得五分位（Q1 → Q5）」.
  Left vertical axis label: 「必需品支出割合」 (bars) — taller bar at Q1, shorter at Q5, monotonically decreasing.
  Right vertical axis label: 「輸入価格ショック影響度」 (line) — line peaking at Q1 and declining toward Q5, mirroring the bars.

X-axis tick labels: Q1, Q2, Q3, Q4, Q5 (Latin letters with numbers, no translation needed).

Legend at top-right with two entries:
  - blue-gray square + 「必需品支出割合（左軸）」
  - navy line + 「輸入価格ショック影響度（右軸）」

Style: minimalist editorial chart. Bars in muted blue-gray (#4a7fa5). Line in navy (#1a2e4a) with small filled circle markers. White background. Both axes labeled in small navy sans-serif text.

Composition: chart fills the panel with generous padding. No grid; minimal tick marks only.

Constraints: schematic illustration only (not real data), flat 2D, no photorealistic textures, no gradients, no 3D bars, no decorative shapes, no marketing tone. Japanese characters MUST be rendered cleanly and accurately — do not produce garbled or fake-looking kanji.

Output: 1100×280 px, pure white background.
```

### s09 — Three-Phase Analytical Framework（3段階分析フレームワーク）

```
A clean, minimal, academic data-flow diagram for a Japanese economics thesis slide showing a three-phase analytical framework. All labels MUST be in Japanese, rendered exactly as specified below using clean Japanese sans-serif typography (Noto Sans JP / Hiragino Sans style). Do not translate or romanize the labels.

Layout: three rows stacked top-to-bottom. Each row = one phase. Each row contains four blocks left-to-right: phase header (left) → 入力 (input) → 処理 (processing) → 出力 (output), connected by short right-pointing arrows.

Phase 1 — phase header label: 「Phase 1 / 所得流出の構造定量化」
  入力: small icons + labels 「産業連関表」 and 「BOJ CGPI 輸入物価」
  処理: a box containing 「輸入含有率 × グループ別価格」
  出力: a box containing 「5グループ別 所得流出額」

Phase 2 — phase header label: 「Phase 2 / 家計消費への帰着」
  入力: small icons + labels 「CPI（消費者物価指数）」 and 「家計調査」
  処理: a box containing 「パネル OLS 価格転嫁推定 / コストプッシュ識別」
  出力: a box containing 「五分位別 実効インフレ格差」

Phase 3 — phase header label: 「Phase 3 / シミュレーション・政策評価」
  入力: a label 「Phase 1・2 のパラメータ」
  処理: a box containing 「IO 価格モデル + マイクロシミュレーション」
  出力: a box containing 「政策シナリオ別 分配効果」

Between rows: small downward arrow indicating Phase 1 → Phase 2 → Phase 3 hand-off.

Section headers above the columns (only on Phase 1 row, applying to all): 「入力」「処理」「出力」 in small uppercase-style navy text.

Style: minimalist boxes with thin navy (#1a2e4a) outlines, blue-gray (#4a7fa5) accents for arrows and secondary text, white background. Each phase header on a navy band on the left.

Composition: three equal-height rows with consistent box geometry. Generous whitespace.

Constraints: flat 2D, no photorealistic textures, no gradients, no 3D, no decorative shapes, no marketing tone. Iconography must be schematic. Japanese characters MUST be rendered cleanly and accurately — do not produce garbled or fake-looking kanji.

Output: 1100×500 px, pure white background.
```

### s03 — Import Price Time-Series（5グループ別 輸入物価の時系列）

```
A clean, minimal, academic line chart for a Japanese economics thesis slide showing 5 import price groups over time. All labels MUST be in Japanese, rendered exactly as specified below using clean Japanese sans-serif typography (Noto Sans JP / Hiragino Sans style). Do not translate or romanize the labels.

Subject: a single line chart with 5 lines showing the trajectory of import prices from 2020 to 2024.
  - horizontal axis tick labels: 2020, 2021, 2022, 2023, 2024
  - vertical axis label: 「輸入物価指数（2020=100）」 with tick labels: 100, 150, 200, 250, 300
  - 5 lines, each labeled at its right end with the Japanese group name:
      - 「エネルギー」: starts at 100 in 2020, sharp rise peaking near 280–290 in 2022, declining to about 200 by 2024 — THIS LINE IS THE MOST PROMINENT
      - 「木材」: rises to about 200 in 2022, declines to about 130 by 2024
      - 「金属」: rises to about 180 in 2022, gradual decline to about 140 by 2024
      - 「化学」: rises to about 180 in 2022, gradual decline to about 140 by 2024
      - 「食料」: gradual rise to about 150 in 2022, plateau near 145–160 through 2024
  - all 5 lines start at value 100 in 2020 (common baseline)

Visual emphasis:
  - the エネルギー line is the focal point: thicker stroke (around 3px) and in muted crimson (#b03050)
  - the other 4 lines are in muted blue-gray (#4a7fa5), thinner (around 1.5px)
  - this asymmetric weighting signals that エネルギー is the dominant shock

Style: minimalist editorial line chart. Navy (#1a2e4a) axes and tick labels, sparse grid (only major horizontal gridlines, very light gray). White background. Compact legend at top-right OR labels written next to the right end of each line.

Constraints: schematic illustration only (not real precise data, but the shape and ordering of the lines must match the description above), flat 2D, no photorealistic textures, no gradients, no 3D, no decorative shapes, no marketing tone. Japanese characters MUST be rendered cleanly and accurately — do not produce garbled or fake-looking kanji.

Output: 1100×360 px, pure white background.
```

### s06 (Optional) — Research Gap Venn（先行研究の3空白）

```
A clean, minimal, academic Venn-style concept diagram for a Japanese economics thesis slide showing the research gap. All labels MUST be in Japanese, rendered exactly as specified below using clean Japanese sans-serif typography (Noto Sans JP / Hiragino Sans style). Do not translate or romanize the labels.

Subject: three partially overlapping circles. Each circle has a small letter (A / B / C) at top and a Japanese label below:
  Circle A — label: 「マクロ規模の交易損失推計」
  Circle B — label: 「インフレの分配効果」
  Circle C — label: 「日本固有の統合モデル」
The triple overlap in the center is highlighted with a very light blue-gray fill and a small label 「本研究」 placed there.

Style: thin navy (#1a2e4a) circle outlines on white background. The triple-overlap area filled with a very light blue-gray (#e8eef5) tint. Text labels in small navy sans-serif.

Composition: three circles arranged in a balanced triangular layout, ample whitespace around. No drop shadows, no gradients.

Constraints: flat 2D, schematic only, no photorealistic textures, no decorative shapes, no marketing tone. Japanese characters MUST be rendered cleanly and accurately — do not produce garbled or fake-looking kanji.

Output: 1000×500 px, pure white background.
```

---

## §4. 実行順序

| # | ステップ | 状態 |
|---|---------|------|
| 1 | YAML 充足（`author.affiliation` = 専修大学経済学部） | ✅ 完了 |
| 2 | §1 必須・推奨修正の適用（#1〜#5・#7・#8） | ✅ 完了 |
| 3 | §1 任意・要確認（#6 / #9〜#14） | ⏸ 保留（#11〜#14 文献誌名一次確認は `docs/literature/` 整備待ち） |
| 4 | 画像生成準備（`slides/assets/` 作成 + プレースホルダコメント挿入） | ✅ 完了 |
| 5 | 画像生成（§3 プロンプトを ChatGPT Image2 へ投入） | ✅ 完了（7 枚、日本語ラベル版） |
| 6 | 画像差し込み（プレースホルダ → `<img>` / CSS 調整） | ✅ 完了 |
| 7 | DESIGN.md "Final Check" | ⏸ 未実施（発表前リハと併せて実施推奨） |
| 8 | 発表前リハ（1200×675 で実機確認・可読性チェック） | ⏸ 未実施 |

### 進捗判断（決定済み）

| # | 該当 | 内容 | 判断 |
|---|------|------|------|
| 15 | s11 Schedule タイムライン全体 | 6月以降の Phase 1〜3 が **未来形** だが内部は完了済 | ✅ **A. 完全未来形維持**。第1回は「まだやってない体」で計画発表の作法を維持し、段階的情報解除で進める。s1b Hook の自前推計は口頭で「概算こんな感じ」と軽く流す。現状を話すと研究がほぼ終わったと示してしまい、ゼミの意義が損なわれるため、未来形のままが適切 |
| 16 | s9 Framework Phase 2 の文言 | 旧 `.flow` テキスト「費目別の価格転嫁率を推定（パネルOLS）」 | ✅ **実質解消済**。s9 を画像のみに変更したため該当文言は消滅。画像内ラベル「パネル OLS 価格転嫁推定」は手法名なので問題なし |

---

## §5. 次回以降への申し送り（再利用ノート）

- このプランは `slide-brushup` スキルの初回適用例。形式は seminar2/3/final でも踏襲する
- Phase A 1-A〜1-D の表構造は不変。Phase B の slot 表も汎用化済み
- 各回の固有事項（数値結果・引用追加等）は §1 の「根拠」列で `docs/` の対応箇所を明示する運用
- スキル仕様の改善余地: Phase A-2 の典拠照合を `docs/literature/` の自動 Grep に強化 → seminar2 で結果数値が増えるタイミングで検討

### seminar1 で監査の枠を超えて実施した拡張（A〜D）

監査結果に加え、deck の起伏とインパクト改善のため以下のスライド拡張を実施。詳細は `docs/DESIGN.md` の各セクションに原則化。

| 案 | 追加・変更 | 関連 docs |
|---|-----------|-----------|
| **A** Hook（数値ハイライト） | 新スライド `s1b` 追加（34.6 兆円・crimson 強調） | DESIGN.md § Hook Slide / Slide Deck Pacing |
| **B** Feasibility | 第1回からは外す判断（seminar2 以降で正式提示） | `docs/feasibility.md` 新規 / DESIGN.md § Feasibility Slide "When to use" |
| **C** Expected Contribution | 新スライド `s10b`（学術 / 政策 / モデル成果物の 3 軸カード） | `docs/contribution.md` 新規 / DESIGN.md § Contribution Slide |
| **D** 時系列折れ線グラフ | s3 を table + chart の 2 カラム構成に再構成 | DESIGN.md § Charts |

加えて以下の DESIGN.md ルール拡張を実施:
- § Color System に **emphasis: muted crimson** 追加（数字・主要結論の専用強調色）
- § Emphasis Usage（per-slide rule）追加（1 強調 / スライド原則・対比軸は 2 例外可）
- § Line Breaks Inside Boxes / Contrastive Information（熟語禁断改行・対比は別段落）
- § Slide Deck Pacing（緩急設計の推奨構造表）
- § Whitespace の補強（grouping を split しない / tail whitespace は OK）
- § Page Indicator（下部中央 / 白枠内 / 薄色）

### seminar1 deck 最終構成（14 枚）

s1 Title → **s1b Hook** → s2 Bg1 → **s3 Bg2 (table+chart)** → s4 Problem → s5 Prior → **s6 Gap (text+venn)** → s7 RQ → s8 Hypothesis → s9 Framework → s10 Data → **s10b Contribution** → s11 Schedule → s12 References

### Final Check 結果

`docs/DESIGN.md` § Final Check の 7 項目すべて PASS:
1. ✅ Each slide about one clear point
2. ✅ Research gap explicit (s6)
3. ✅ Research question visible (s7 navy box)
4. ✅ Data and method concrete (s10 table + s9 framework)
5. ✅ Readable within a few seconds
6. ✅ Visual tone academic and restrained（navy / blue-gray / white + crimson(emp) + orange(caution)）
7. ✅ Overall structure logically progressive

### 文献一次照合（s5 / s12）

`docs/literature/` の paper ファイルと完全照合し、s12 References 全 12 件を正規化済。s5 の Sato 2024 は文脈ミスマッチ（経常収支論文を製造業海外移転の文脈で引用）のため削除。
