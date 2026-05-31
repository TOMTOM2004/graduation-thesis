# TODO — 卒業論文（案B）

_Last updated: 2026-05-31 / session: 案2 却下（DEC-013）+ Phase 3 を定性・例示に降格（DEC-014）_

## 🎯 Next action（1つだけ、具体的に）
- What: **論文執筆に着手** — Phase 1（会計）/ Phase 2b（恒等式逆進性）を背骨に、Phase 2a（識別限界明記）と Phase 3（定性・例示 incidence accounting）を従に配置。まず先行研究レビューか方法論の章から
- Where: 論文ドラフト（保存先未定・要決定）/ `docs/` の各設計ドキュメントを素材に
- Done when: 章立て確定＋1章分の初稿。または指導教員フィードバック対応の準備

## ✅ 直近完了（2026-05-31・このセッション）
- **案2 却下（DEC-013/A-5）**: 両 estimand とも期間延長は識別を救わない。①group-specific β_g は共線性で分離不能、②pooled β は CPI 2005延長で直接再推定→FD-Koyck δ=0.55・two-way FE で両窓非有意（level-anchoring・単一集計shifterは time FE が時間変動吸収し識別が IC固定依存）。途中2誤りを advisor catch で訂正（pr_group のみ測り誤却下しかけ／CPI を e-Stat 全 tab_code 平均で汚染→overlap照合 tab_code==1 で修正）。再現: `tasks/_an2_shock_independence.py`, `tasks/_an2_pooled_fd.py`
- **Phase 3 を定性・例示に降格（DEC-014）**: G-3 は既に解消済（fresh再生成=cache 完全一致）。モデルが overshoot（cost-push 平均5.2pp > 実績~2.5%＝C-4 構造ミスマッチ・β=0.431 でも残る）、政策削減率が B-4 IC是正で ~101.6%→44.7% と IC依存で激変（β はキャンセルするが β-invariant≠robust）。**特定%・pp 絶対値は結論にせず incidence accounting/例示で appendix**。結論に残すのは符号レベル（Q1>Q5・energy 最大寄与・補助は方向として gap 縮小）。再現: `tasks/_phase3_recalib_check.py`
- **重要な含意**: headline を支えていた Phase 2a(回帰)と Phase 3(IO sim)が想定より弱いと連続判明＝硬い背骨は Phase 1(会計)+Phase 2b(恒等式)。合意方針の正しさが裏付けられた
- **貢献を再定義（DEC-015）**: DEC-008 が掲げた「コストプッシュ/デマンドプル識別」は本設計・データで不可能と判明→**失敗でなく識別限界の方法論的提示という貢献に転化**。再定義した4貢献=①交易損失の会計的定量化②逆進性の恒等式記述(背骨)③識別限界の方法論的提示(exposure-robust shift-share+期間延長テスト)④統合シミュレーション(例示)。overview/research-design/decision-log 更新済。**project `.claude/CLAUDE.md` Phase2 サマリーの更新は self-modification 判定で保留＝ユーザー承認待ち**

## 📍 State snapshot
- ✅ Done（メインブランチ `claude/20260526-seminar1-script`・**origin push済**）:
  - `docs/design-review.md` 学術監査（A/B/C/D/G項目）、G-2(家計universe=二人以上, DEC-011)、G-1(交易損失中心~35兆/上限40.7兆, DEC-012)、Phase 2a framing整理(因果→整合的・プラセボsupported撤回)、Phase3 caveat、文献P077-P080
- ✅ Done（実験ブランチ `claude/20260531-a4-groupspecific-shiftshare`・**未push**・f9e9b21）:
  - B-4(IC>1是正・競争輸入型 μ^T(I-(I-M̂)A)^-1) + A-4(group-specific shift-share) + AKM SE(R `ShiftShareSE` を `~/.Rlib` にインストール済)
  - **結論: βの点推定は頑健(0.43・energy/food主導)だが AKM0 で有意性崩壊(p≈0.15)。根本=独立な輸入物価ショックが実質1つ(少数実効ショック)**
- 🟡 In progress: なし（案2 却下・Phase 3 降格 済・次は論文執筆）
- 🔴 Blocked: なし

## 🧠 Context not in code（次セッション必読）
- **βの正体**: 年・費目FEで二元除去後の**単一スロープ**（IC/P_importは単独で入らず交差項のみ）。β=転嫁率。有意取れない根本は計算でなく「独立ショックが実質1つ(2021-24サージ)」＝**設定に内在・別の回帰では直らない**。
- **立っているもの（β/回帰に非依存・無傷）**: Phase 2b(Q1-Q5 +1.42pp逆進性＝実績CPI×実シェアの恒等式)、Phase 1(~35兆＝会計)。**卒論の実証背骨はこれ**。
- **方針合意**: 重心を Phase 2b(記述・堅い)に、Phase 2a は識別限界を正直に明記、Phase 3 は較正して例示的に。「レベル下げ」でなく誠実で高度な構成。
- **案2 は却下（DEC-013・実データ検証済）**: ①group-specific β_g は共線性で分離不能。②pooled β を CPI 2005延長で直接再推定→FD-Koyck δ=0.55・two-way FE で両窓非有意（level-anchoring現象）。単一集計 shifter は time FE が時間変動を吸収し識別が IC(2020固定)依存のため、期間延長は効かない。重心は Phase 2b（恒等式・β非依存）/Phase 1（会計）。Phase 2a は識別限界を鋭利化して明記。

## ❌ Don't do (this task)
- [trap] 有意性回復のため「月次化・費目増で母数(n)を増やす」のは無効（観測非独立、AKM0が織り込み済）。効くのは独立ショック事象を増やすことだけ
- [trap] Phase 2a の β を「因果的に実証/有意に識別」と書かない（exposure-robust推論では非有意）。「cost-pushと整合的な点推定」に留める

## ❓ Open questions for user
- [ ] 実験ブランチ `claude/20260531-...` を push/PR するか（B-4 IC是正 + A-4 + 案2 feasibility 判定は main系マージ価値あり。group-specific 異質性の負の結果と 2軸 feasibility は論文の識別限界節の根拠として残す）
- [x] 案2 を進めるか → 実データで検証し **却下**（DEC-013）。次は ③ Phase 3 再較正(C-4)

## 📂 Key files
- `docs/design-review.md`（全監査・A-5案2判定）/ `docs/decision-log.md`（DEC-011/012/013）
- `src/utils/io_utils.py`（B-4 IC是正・実験ブランチ）/ `src/analysis/cost_push_panel.py`（β回帰）
- `tasks/_a4_groupspec.py` `tasks/_a4_akm.R`（A-4・AKM再現）/ `tasks/_an2_shock_independence.py`（案2ショック独立性検証）
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
- ❌ **案2: 識別の立て直し（期間延長）→ 却下（DEC-013/A-5・2026-05-31・実データ検証済）**。group-specific は共線性で分離不能、pooled は CPI 2005延長で直接再推定し FD-Koyck δ=0.55・two-way FE で両窓非有意。単一集計 shifter は time FE が時間変動を吸収し識別が IC(2020固定)依存→期間延長は効かない。IO表3版再構築(D-3)は識別改善せず不着手。再現: `tasks/_an2_shock_independence.py`, `tasks/_an2_pooled_fd.py`
- ✅ **③ Phase 3 → 定性・例示に降格で完了（DEC-014）**。点較正/財別較正は A-5（β_g 識別不能）と循環性で却下。代わりに minimal-honest-fix（C-1 incidence accounting・C-4 β=1上限/×0.431例示・C-2 RMSE分解・C-3 δ calibration）＋数値降格。特定%・pp は結論にせず符号レベル(Q1>Q5・energy 最大寄与・補助は方向)のみ結論。再現: `tasks/_phase3_recalib_check.py`
- ✅ **Koyck整合性（G-3+C-2+C-3）→ 既に解消済を確認（DEC-014）**。io cache を δ=0.55 で force 再生成→現 cache と完全一致(diff=0)・koyck≠empirical 確認。実験ブランチ f9e9b21 が既に正しく再生成済で design-review G-3 のテキストが stale だった。下流(policy/microsim) は coherent δ=0.55 で再生成済
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
