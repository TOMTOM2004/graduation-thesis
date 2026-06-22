# TODO — 卒業論文（案B）

_Last updated: 2026-06-22 12:48 / session: 産業空洞化アイデア探索（反証）→ 副産物を本論ドラフトに組込み・図表日本語化_

## 🎯 Next action
- What: 第2回ゼミ発表の準備（テーマは未確定。提出が論文かスライドか次第で方針分岐）
- Where: `paper/01-introduction.md`（序論ドラフト） / Issue #8（スライド化検討）
- Done when: 第2回発表で何を出すか方針を決め、序論の国際比較をスライド or 本論のどちらに展開するか確定

## 📍 State snapshot
- ✅ Done（今セッション）:
  - 研究アイデア「産業空洞化→インフレの質」を探索ブランチで検証 → **反証**（PR #7）
    - 単一国時系列×コストプッシュ比率DV: 分母≈0で不成立（DEC-IDEA-01）
    - クロスカントリー46ヶ国2022×交易損失DV: 製造業シェア係数が正で頑健（仮説と逆, DEC-IDEA-02）
  - 副産物（交易損失の国際比較・日本9位/46）を本論ドラフトに組込み: `paper/01-introduction.md`・`paper/04a-...`・`paper/outline.md`
  - 図1.1/1.2/表1.1 を生成・**図内国名を日本語化**・本文にキャプション番号付与
  - Issue #8（スライド化の検討）作成
- 🟡 In progress: なし
- 🔴 Blocked: なし（提出形態の確定待ち＝ユーザー判断事項）

## 🧠 Context not in code
- 決定: 探索仮説は反証だが本論レベルは下げない。確実な「エネ/輸入依存→所得流出, 日本高位」のみ本論に採用。製造業反証は第7章考察に留保（第2回ゼミ後）
- 決定: 副問1本体（34.6兆円本文）は提出形態未確定のため保留
- 参考: 図の正規番号は序論に置く（hook=主）。副問1ベンチマークは序論既出として参照
- 数値: 日本は交易条件悪化-17.9%が標本中最大だが損失%GDPは9位（開放度37%が中位のため）

## ❌ Don't do (this task)
- [trap] サンドボックスで Python urllib/socket は timeout するが curl は通る → 外部 API は curl でローカル保存し Python はローカル読み
- [trap] `.env` への grep は classifier が拒否（Read(.env) deny の迂回扱い）。回避せず bool 確認かアプリ側ローダ経由で
- [trap] クロスカントリーで「インフレに占めるコストプッシュ比率」DV は低インフレ国・年で分母≈0となり発散。share系DVは持続的インフレが前提
- [mistake] 反証された仮説（製造業=耐性）を本論に持ち込まない。確実な発見のみ採用し反証は限界節へ

## ❓ Open questions for user
- [ ] 第2回ゼミ発表で何を出すか（テーマ確定）
- [ ] 提出は論文かスライドか（→ 副問1本体執筆の要否が決まる）

## 📂 Key files
- `paper/01-introduction.md` / `paper/04a-subq1-international-benchmark.md` / `paper/outline.md`
- `docs/research-ideas/deindustrialization-inflation.md`（探索の全証跡・DEC-IDEA-01/02）
- `src/analysis/deindustrialization{,_xc,_fig}.py`
- `data/processed/deindustrialization/`（図1.1/1.2/表1.1）

## ❌ Out of scope（今セッション）
- 副問1本体の執筆（提出形態確定後）
- 第7章 考察での製造業反証の記述（第2回ゼミ後）
- スライド化（Issue #8 に退避）

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

---

## スライドレイアウト修正（`slides/20260520-seminar1-proposal.html`）

### 課題

| # | 現象 | 原因 |
|---|---|---|
| 1 | 枠（ボックス）内の余白が多く、図として締まりがない | `.fw-box`・`.hyp-step`・`.col-box`・`.rq-main` 等の padding が 20–32px と大きい。スライド外周 padding も 50px/68px で二重に余白が生じている |
| 2 | 文字が小さくスライド全体のバランスが悪い／余白が目立つ | ボックス内テキストが 11–14px（DESIGN.md の最小 15px ルール違反）。小さな文字 + 大きな padding の組み合わせが「空箱に豆文字」状態を作っている |

### 修正方針

1. **テキストサイズの底上げ**
   - ボックス内本文（`.flow-box ul li`・`.fw-box ul li`・`.col-box ul li`・`.lit-card ul li`・`.hyp-step p` 等）: 13–14px → 15px
   - セクションラベル（`.flow-box h3`・`.fw-box .fw-phase`・`.section-tag`・`anchor-label` 等）: 11px → 13px
   - サブタイトル・カード見出し: 13px → 14–15px

2. **ボックス padding の圧縮**
   - `.fw-box`・`.flow-box`・`.hyp-step`: `20–22px 18px` → `14px 16px`
   - `.col-box`: `20px 22px` → `14px 16px`
   - `.lit-card`: `16px 18px` → `12px 15px`
   - `.rq-main`: `28px 32px` → `18px 24px`
   - `.sub-rq-card`: `16px 15px` → `12px 14px`

3. **スライド外周 padding の調整**
   - 現在: `50px 68px 40px` → `40px 56px 32px`（左右の二重余白を緩和）

4. **修正後の検証観点**
   - 各スライドで枠とテキストの密度バランスが取れているか
   - DESIGN.md「最小 15px」ルールをすべての本文要素が満たしているか
   - スライドを 80% 縮小しても読めるか

### タスク

- [ ] ブランチ `claude/fix-slide-layout` で修正 HTML を作成
- [ ] 全 12 スライドを目視確認
- [ ] DESIGN.md Final Check を実施
- [ ] main へマージ

---

## 研究アイデア

_（産業空洞化→インフレの質 のアイデアは探索完了・反証。`tasks/done/2026-06.md` 参照）_
