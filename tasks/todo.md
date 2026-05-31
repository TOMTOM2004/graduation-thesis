# TODO — 卒業論文（案B）

_Last updated: 2026-05-31 / session: 設計レビュー＋G-1/G-2/framing修正＋A-4実験（β有意性のAKM検証）_

## 🎯 Next action（1つだけ、具体的に）
- What: 案2（識別の立て直し）の **feasibility 確認** — 古いCGPI長期連結・2005/2011/2015 IO表・家計調査の**遡及取得可否**を調べる。取得できれば期間延長で独立ショック(2008原油/2011福島/2014-16暴落/2008-12円高)を ~1→~3-4 に増やせる
- Where: `estat-search` skill / `src/data/` fetch スクリプト / `docs/design-review.md` A-3,A-4
- Done when: 古いデータの取得可否・粒度が判明し、案2に本格着手するか別方針かを判断できる

## 📍 State snapshot
- ✅ Done（メインブランチ `claude/20260526-seminar1-script`・**origin push済**）:
  - `docs/design-review.md` 学術監査（A/B/C/D/G項目）、G-2(家計universe=二人以上, DEC-011)、G-1(交易損失中心~35兆/上限40.7兆, DEC-012)、Phase 2a framing整理(因果→整合的・プラセボsupported撤回)、Phase3 caveat、文献P077-P080
- ✅ Done（実験ブランチ `claude/20260531-a4-groupspecific-shiftshare`・**未push**・f9e9b21）:
  - B-4(IC>1是正・競争輸入型 μ^T(I-(I-M̂)A)^-1) + A-4(group-specific shift-share) + AKM SE(R `ShiftShareSE` を `~/.Rlib` にインストール済)
  - **結論: βの点推定は頑健(0.43・energy/food主導)だが AKM0 で有意性崩壊(p≈0.15)。根本=独立な輸入物価ショックが実質1つ(少数実効ショック)**
- 🟡 In progress: 案2（期間延長で独立ショック増）の検討。feasibility 未確認
- 🔴 Blocked: なし

## 🧠 Context not in code（次セッション必読）
- **βの正体**: 年・費目FEで二元除去後の**単一スロープ**（IC/P_importは単独で入らず交差項のみ）。β=転嫁率。有意取れない根本は計算でなく「独立ショックが実質1つ(2021-24サージ)」＝**設定に内在・別の回帰では直らない**。
- **立っているもの（β/回帰に非依存・無傷）**: Phase 2b(Q1-Q5 +1.42pp逆進性＝実績CPI×実シェアの恒等式)、Phase 1(~35兆＝会計)。**卒論の実証背骨はこれ**。
- **方針合意**: 重心を Phase 2b(記述・堅い)に、Phase 2a は識別限界を正直に明記、Phase 3 は較正して例示的に。「レベル下げ」でなく誠実で高度な構成。
- **案2の核心**: n増≠識別改善。独立ショック事象増だけが効く。期間を~2005-08へ延ばすと複数独立事象を取り込め実効ショック~3-4。前提=①IC時間不変悪化→期間対応IO表で時変IC化(D-3も是正)②β安定性(構造変化跨ぎ)③データ整備。非有意でも「複数独立ショックでなお非有意＝効果は頑健に不確実」はより強い結論。

## ❌ Don't do (this task)
- [trap] 有意性回復のため「月次化・費目増で母数(n)を増やす」のは無効（観測非独立、AKM0が織り込み済）。効くのは独立ショック事象を増やすことだけ
- [trap] Phase 2a の β を「因果的に実証/有意に識別」と書かない（exposure-robust推論では非有意）。「cost-pushと整合的な点推定」に留める

## ❓ Open questions for user
- [ ] 案2（期間延長＋時変IC）に投資するか。まず feasibility 確認でよいか
- [ ] 実験ブランチ `claude/20260531-...` を push/PR するか（B-4 は main系マージ価値あり）
- [ ] Phase 3 再較正(🔴)と 案2 のどちらを先に着手するか

## 📂 Key files
- `docs/design-review.md`（全監査）/ `docs/decision-log.md`（DEC-011/012）
- `src/utils/io_utils.py`（B-4 IC是正・実験ブランチ）/ `src/analysis/cost_push_panel.py`（β回帰）
- `tasks/_a4_groupspec.py` `tasks/_a4_akm.R`（A-4・AKM再現）
- `docs/literature/papers/{moreno-louzada-etal-2025,borusyak-hull-jaravel-2024,bhattarai...,cicero...}`（P077-P080）

## ❌ Out of scope（当面）
- seminar2/3/final 用スライド（時期到来時に slide-brushup）
- Paasche化・G-4価格表記・スライド運用ルール（下記残タスク）

---

## 残タスク

### 設計レビュー由来（`docs/design-review.md` / DEC-011・012）
- ✅ G-2 家計調査 universe を二人以上に確定・cat02 明示フィルタ＋潜在バグ除去（DEC-011, 負担数値は不変）
- ✅ G-1 交易損失を中心推計C（2015-19正常基準）に統一・中心~35兆／上限40.7兆（DEC-012）
- ✅ ① Phase 2a 識別の framing 整理（因果→整合的関連、プラセボ supported 撤回→年次相関主証拠、goods-services 交絡明記）。research-design.md に「識別の到達点と限界」節を新設し INDEX/overview/contribution/feasibility/CLAUDE/decision-log を統一
- ✅ B-4 輸入含有率 IC>1 是正（競争輸入型 μ^T(I-(I-M̂)A)^-1, `io_utils.py` 修正・IC>1解消）【実験ブランチ f9e9b21】
- ✅ ② A-4 group-specific shift-share 実装（IC_{c,g}×P_{g,t}）+ AKM exposure-robust SE。**結論: energy/food はクリーン識別だが点推定のみ頑健、AKM0 で有意性崩壊(p≈0.15)＝少数実効ショック**【実験ブランチ・未push】
- [ ] **🌟 案2: 識別の立て直し（期間延長＋時変IC）** ← 次の主戦場。対象期間を~2005-08へ延長し独立ショック事象(2008原油/2011福島/2014-16暴落/2008-12円高=2022逆符号)を取込み実効ショック~1→~3-4。前提=①期間対応IO表(2005/2011/2015/2020)で時変IC化(D-3是正)②β安定性検証③古いCGPI/IO/家計調査の取得。**まず feasibility 確認から**（Next action 参照）。世界価格vs為替の分解(案1)は案2と組んで初めて効く
- [ ] **③ Phase 3 を cost-push 成分に再較正（C-4 根本変更）**: ×β スケーリングを廃し、Phase 2a が定義する cost-push CPI に対し転嫁率＋動学を**財/グループ別に較正**（日本2021-24 への calibration 許容）。総合CPIは追わない（需要モジュールは decouple・将来拡張）。Leontief 構造は維持。下の「Phase3 Koyck再生成」はこの一部に統合。ただし β の識別が弱いと判明したので較正の的の信頼性は案2の結果次第
- [ ] **🔴・Phase 3 再構築の一部】Koyck整合性の再生成（G-3+C-2+C-3）**: `io_price_model_output.csv` の `delta_cpi_koyck_pp` が全ショック年で `delta_cpi_empirical_pp`（瞬時値・δ=1相当）と一致＝**δ=0.55 の Koyck が cache に未適用**。headline（格差0.10/0.32/0.38/0.41・政策101.6%/123.8%・RMSE 9.744「δ=0.55」）が実質δ=1.0で計算されている。手順=①`run_io_price_model_all_years` 監査(stale or bug)→②δ=0.55・force再生成し koyck≠empirical 確認→③下流(microsim/policy_comparison/sensitivity)全再生成→④main/感度の41→10集約経路統一(D-4)→⑤headline再導出しdocs更新。**headlineが変わるため要承認**（design-review G-3 参照）
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
