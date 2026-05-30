# TODO — 卒業論文（案B）

_Last updated: 2026-05-26 / session: seminar1 発表原稿（約15分・話し言葉）作成・push_

## 🎯 Next action
- What: 5/20 ゼミ発表前のリハーサル（原稿を読み上げて 15 分に収まるか計測・ペース調整）
- Where: `slides/20260520-seminar1-script.md` ＋ `slides/20260520-seminar1-proposal.html`
- Done when: 通し読みで時間内に収まることを確認、押す/余る場合は原稿末尾「補足メモ」の増減候補で調整

## 📍 State snapshot
- ✅ Done（今セッション）:
  - seminar1 発表原稿を新規作成（全 14 枚に 1:1 対応・話し言葉・スライド転換合図・トーン指示・ペース配分メモ）
  - 第1回=計画発表のため数値は「推計/試算/目安」と明示し断定を回避
  - proposal.html の発表者名修正（石田友典 → 石田智識）
  - ブランチ `claude/20260526-seminar1-script` に 2 コミット（49d3fad 原稿 / b0f06a6 名前修正）、origin に push 済
- 🟡 In progress: なし
- 🔴 Blocked: なし
- 📌 未了: PR 未作成（push のみ。必要なら次セッションで作成）

## 🧠 Context not in code
- 進捗判断: s11 Schedule は計画形維持（第1回は "まだやってない体" で口頭補足する戦略）
- 原稿も計画発表の建前に統一（確定結果を断定せず推計扱い）
- emphasis 色 muted crimson `#b03050` を新規追加（caution=orange と役割分離）
- 第1回で Feasibility は出さない方針（seminar2 用に `docs/feasibility.md` 温存）
- 任意未対応: #6 s10 の貿易統計（概況品別国別表）追加 — 第1回は省略

## ❌ Don't do (this task)

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

### 設計レビュー由来（`docs/design-review.md` / DEC-011・012）
- ✅ G-2 家計調査 universe を二人以上に確定・cat02 明示フィルタ＋潜在バグ除去（DEC-011, 負担数値は不変）
- ✅ G-1 交易損失を中心推計C（2015-19正常基準）に統一・中心~35兆／上限40.7兆（DEC-012）
- [ ] **🔴最優先・別セッション】Phase 3 Koyck整合性の再生成（G-3+C-2+C-3）**: `io_price_model_output.csv` の `delta_cpi_koyck_pp` が全ショック年で `delta_cpi_empirical_pp`（瞬時値・δ=1相当）と一致＝**δ=0.55 の Koyck が cache に未適用**。headline（格差0.10/0.32/0.38/0.41・政策101.6%/123.8%・RMSE 9.744「δ=0.55」）が実質δ=1.0で計算されている。手順=①`run_io_price_model_all_years` 監査(stale or bug)→②δ=0.55・force再生成し koyck≠empirical 確認→③下流(microsim/policy_comparison/sensitivity)全再生成→④main/感度の41→10集約経路統一(D-4)→⑤headline再導出しdocs更新。**headlineが変わるため要承認**（design-review G-3 参照）
- [ ] **【別セッション】Paasche/Fisher 化**: `trade_loss.py` を固定数量(Laspeyres, 2020輸入額固定)→実数量へ精緻化。前提＝**財務省貿易統計の数量データ取得**（現状 raw は衣類のみ）。`src/data/fetch_trade_stats.py` を拡張し5グループの品目別 数量×価額を取得 → 価格効果を q_t ベースで再計算
- [ ] **【別セッション】G-4 エネルギー価格上昇率の表記ゆれ**: +203%（年平均集計・再現可）vs +213〜286%（research-design.md/slides・品目別ピーク?・リポジトリのデータで再現不能、286は集計月次ピーク268超）。品目別ピークの一次ソースを示すか +203%(年平均)/+268%(月次ピーク) に統一
- [ ] **スライド運用ルールの策定**: 現状 `slides/` に HTML 直置きで命名規則・格納が未定。決めること = ①命名規則（`YYYYMMDD-<発表名>.html` 等・版管理）②格納構成（回ごとサブディレクトリ／`assets/` の配置）③proposal.html・script.md・brushup-plan.md の対応関係の規約化 ④**発表済スライドの凍結方針**（例: seminar1 の hook は提示記録として 34.6 のまま保持、35兆は seminar2 以降に適用）。規約は `docs/DESIGN.md` か `.claude/slide-context.yaml` に記録

### 執筆前準備
- [ ] 非線形モデルの扱いを明確化（research-design.md に「線形・非線形を比較」と記載。結果は線形のみ → 非線形を試した結果を記録するか、未実施の理由を DEC に追記）
- [ ] Koyck δ=0.55 の選定根拠を文書化（新規DEC として decision-log.md に追記。design-review C-3: 独立gridでは RMSE最小は δ=0.60、曲面は[0.5,0.7]で平坦＝弱識別。「推定」でなく calibration と明記し半減期≈10.4ヶ月の根拠を示す）
- [ ] 先行研究との数値比較表を作成（β=0.431 vs Yagi et al. / Amiti-Itskhoki-Konings、交易損失 中心35兆円（上限40.7）vs 齊藤 2022 / 内閣府推計。ロバストネス appendix 用）
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
