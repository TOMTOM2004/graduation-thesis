# TODO — 卒業論文（案B）

_Last updated: 2026-06-25 / session: ブランチ統合をmainへマージ完了(PR#9) + 問題意識2枚を第2回デッキへ統合 + 全featureブランチ削除_

## 🎯 Next action（1つだけ、具体的に）
- What: **第2回発表(6/26)のリハーサル**（実機 1200×675 で `slides/20260626-seminar2-results.html` を通し・時間計測〜15分）。問題意識2枚＋本編10枚＋巻末バックアップ1枚＝13枚の流れを確認
- Where: スライド `slides/20260626-seminar2-results.html` + 原稿 `slides/20260626-seminar2-script.md`（原稿は問題意識2枚ぶん未追記＝要更新）
- Done when: 6/26 発表の通しリハ済・時間内に収まる確認
- 別線: ① 第3回/第4回 原稿(script.md)作成判断 ② 論文執筆着手（実証3本柱を結果章に統合）

## ✅ 直近完了（2026-06-25・このセッション・統合mainマージ＋Issue#8）
- **ブランチ統合をmainへ（PR#9 マージ済）**: 本筋 `0613`（Phase2/三角測量/seminar2-4デッキ）＋副産物 `0621`（産業空洞化探索の反証＋国際比較）を consolidate 経由で main へ統合。祖先 `0526`/`0531` 含む**全 feature ブランチを削除**（local+origin）→ ブランチは main のみ。競合は `todo.md` 1ファイルのみ解消
- **Issue #8 解消（最終）**: 産業空洞化の副産物（国際比較・日本9位/46・3.28%GDP・-17.9%最大級・エネ依存R²=0.64）を問題意識2枚スライドにし、**第2回デッキ `20260626-seminar2-results.html` 冒頭の動機づけに統合**。散布図の橋渡し(①規模→②帰着→③政策)が35兆hook→3本柱へ接続。-17.9%曝露は巻末バックアップ。独立デッキ `20260625-...` は廃止（図資産 `s2b-*.png`・生成 `deindustrialization_fig_slide.py` は保全）。論文序論にも組込み済
- **ランキング図の可読化**: 縦長46行→2カラム横長（`deindustrialization_fig_slide.py`）でスライド尺でも国名可読。日本注記は棒位置に「◀ 日本 3.28%GDP」、縦軸ラベル左揃え
- **方針確定（第2回=中間発表-1）**: 第2回/3回/4回=中間-1/中間-2/最終。中間発表は研究全体アーク再提示の場＝動機づけ必須。国際比較の枚数は発表が進むほど縮小（中間-1で2枚→以降1枚→巻末）、フルは論文序論
- **副産物の探索記録**: 単一国時系列×コストプッシュ比率DVは分母≈0で不成立（DEC-IDEA-01）。クロスカントリー46ヶ国×交易損失DVは製造業シェア係数が正で頑健＝仮説と逆（DEC-IDEA-02）。反証仮説（製造業=耐性）は本論に持ち込まない。証跡 `docs/research-ideas/deindustrialization-inflation.md`

## ✅ 直近完了（2026-06-13・このセッション・3回分のスライド草案）
- **第2回ゼミ発表スライド完成（6/26発表・〜15分）**: `slides/20260626-seminar2-results.html`（10枚）+ `slides/20260626-seminar2-script.md`（原稿・Q&A準備込み）。DEC-017 Tier1/Tier2 を背骨に「3本の硬い柱＋正直なピボット」を構成。advisor の框A/B/C を反映（①ピボットを正面から所有 ②+1.42pp=実効インフレ逆進性≠cost-push単独 ③「識別でなく三角測量」明示）。headless Chrome で全枚描画検証。s7/s8 のレイアウト修正（3カラム枠統一・ブロック縦中央化）も実施
- **第3回ドラフト作成（論文ドラフト全体・15枚）**: `slides/20261101-seminar3-draft.html`（日程未定で日付暫定）。章構造（背景→RQ→方法→結果→考察→限界→結論）で seminar2 と差別化。ADD=考察・先行研究数値比較(placeholder)・ロバストネス・限界形式化・未解決点提示。トーン「完成形だが wet」
- **第4回骨格作成（最終・結論・13枚）**: `slides/20270115-seminar4-final.html`（骨格＋placeholder）。ナラティブの弧「約束→ピボット→届けた答え」を背骨に、4貢献確定・政策含意・結論。第3回フィードバック応答は placeholder スライドで枠だけ。未確定数値は ph バッジ
- **全3デッキ共通の framing**: RQ は DEC-015 再定義版（clean識別を前提にしない）で統一。seminar2 CSS フレームワーク流用
- **重要**: 全作業がブランチ `claude/20260613-seminar2-slides` に集約・**未push**。seminar1 hook 34.6 は提示記録として保持、35兆は seminar2 以降に適用（凍結方針通り）

## ✅ 直近完了（2026-06-03・仮説×証拠 監査→クレーム階層化）
- **DEC-017 provable 優先のクレーム階層化（ユーザー承認）**: 全クレームを証拠ステータスで監査し2層化。**Tier 1（背骨・全て repo 証明済・回帰/消費応答識別に非依存）**: 交易損失~35兆（会計）→ H1/H2 必需品=高輸入含有（食料 Q1-Q5 +8.3pp・光熱 +4.8pp・**今回 repo 実測**）→ +1.42pp 実現インフレ逆進性（恒等式）→ Shapiro 層1 供給主導(0.70)。**Tier 2（誠実な副次）**: 識別限界(2a/層2 null=貢献③)、統合シミュ(Phase3=④)。
- **doc 整合済**: decision-log DEC-017 / overview「貢献の核」に Tier1 連鎖 / research-design 仮説節に H1-H4 ステータス＋repo 証拠 / contribution.md 空白②再文言＋冒頭バナー（β=0.431 を Tier2 に降格明示）。
- **要点**: +1.42pp は**実現インフレ逆進性**（最頑健）であって cost-push 単離でない（不可能・DEC-013）。H2＋層1 で cost-push へ三角測量的に橋渡し。heterogeneity の核は +1.42pp 1本依存＝意識的決定。

## ✅ 直近完了（2026-06-01・このセッション・層2 Shapiro）
- **層2 group-specific 実装完了（DEC-016 層2・`src/analysis/shapiro_quintile.py`）**: ν^p 共通を GATE assert で確認（設計 crux 成立）。**判定=INCONCLUSIVE**: pre-registered 仮説 Q1>Q5 は per-year で 2/4 shock years のみ成立（2022-23 コア cost-push 年で逆転）、pooled +0.043 は 2021+2024 由来。年次×五分位の粗さで数量応答マージン解像不能＝誠実な null。**Phase 2b（実効インフレ gap・ウェイトベース）は無傷**。crux framing: 「Q1 がより収縮的消費応答」も robust に言えず（≠ cost-push exposure・ν^p 共通）

## ✅ 直近完了（2026-06-01・このセッション・層1 Shapiro）
- **層1 Shapiro 実装完了（DEC-016 層1・詳細 `docs/shapiro-decomposition.md`）**: `src/analysis/shapiro_decomp.py`。crosswalk 116品目・VAR残差化+月連続性マスク・**インフレ寄与加重**集計（Shapiro P081）。バスケット=116 物理数量 食料+家庭用エネルギー品目。**headline=supply-driven SHARE**: 2021 0.41(需要主導)→2022 0.70(供給surge)→2024 0.83。**2021需要→2022供給転換が Shapiro米国・timeline と整合**、月次で侵攻(2022/2)から跳ね上がり。2022 supply 寄与 broad(top5=43%・筆頭ガソリン/鶏肉/さけ)。5 spec・balanced 105(0.42→0.72)・生鮮除外(0.42→0.76)で robust。
- **framing 訂正（advisor reconcile）**: 当初「price-YoY が食料CPI一致」は buggy calc 由来で**撤回**。basket は公式食料CPIを構造上 tracking しない（2023 公式+8.06 vs basket+3.99）＝外食/調理/加工欠落・エネ含む。**乖離は feature**＝ラグ付き転嫁＝cost-push 整合。スコープ厳守:「basket 内 2022 供給surge」ship／「食料インフレ X% 供給駆動」書かない。pp 寄与=内部denominator(Dec-to-Dec)。
- **pre-registration 記録（DEC-016 補遺）**: 価格=CPI主/unit-value頑健性、残差化=月次VAR+季節（advisor で AR→VAR 精緻化）、framing「供給駆動≠輸入cost-push」。split を見る前に固定

## ✅ 直近完了（2026-05-31〜06-01・このセッション・実験ブランチ未push）
- **案2 却下（DEC-013/A-5）**: 両 estimand とも期間延長は識別を救わない。FD-Koyck δ=0.55 two-way FE で両窓非有意。再現: `tasks/_an2_shock_independence.py`, `_an2_pooled_fd.py`
- **Phase 3 降格（DEC-014）**: overshoot(5.2pp>実績2.5%)・政策率 IC依存(101.6%→44.7%)・β-invariant≠robust → 定性/例示。符号レベルのみ結論。再現: `tasks/_phase3_recalib_check.py`
- **貢献を再定義（DEC-015）**: cost-push/demand-pull 識別は不可能と判明→識別限界の方法論的提示を貢献に転化。4貢献に再定義。docs統一・CLAUDE.md Phase2 反映済(承認済)
- **ウクライナ小麦 LATE（KEEP）**: 事前ルールで判定。ITS で小麦 pre-trend flat(+0.037%/月)＋2022/2 break +4.62%＋post単調→ 存在証明成立。米controlは非平行ゆえ ITS。副産物=cost-push 食料全般に広い。再現: `tasks/_ukraine_eventstudy.py`, `_ukraine_wheat_scope.py`
- **インフレ時系列整理**（`docs/inflation-timeline.md`）: 日本は2020-21デマンドプル不在(財vsサービス・実質賃金3年連続マイナス・需給ギャップ)＝cost-push主導。エネは2021先行・2023補助で抑制
- **Shapiro 採用（DEC-016）**: 文献(P081-084)で cost/demand 分離は Shapiro で清浄control不要と判明→採用。2層(national月次/quintile年次=novel)。データ表ID特定・構造検証済

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
- [x] 実験ブランチ `claude/20260531-...` を push/PR するか → **2026-06-25 consolidate に統合**（0531/0526 は 0613 内包。全作業を consolidate→main で main系に集約）。group-specific 負の結果と 2軸 feasibility は識別限界節の根拠として残す
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

- [ ] # claude-brain
情報の引き出し方が上手くできてるかの調査とアップデート
RAGにおける先行研究の調査も併用する。（Slack #todo より _2026-06-23_）
